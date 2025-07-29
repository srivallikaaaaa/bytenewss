from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse

import logging

from .models import Article, Category, UserPreference, ReadingHistory, SummaryFeedback
from .utils import generate_summary

logger = logging.getLogger(__name__)


class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.all().order_by('-published_date')
        category = self.request.GET.get('category')
        query = self.request.GET.get('q')

        if category:
            queryset = queryset.filter(category__name__iexact=category)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()

        if self.request.user.is_authenticated:
            try:
                preferences = self.request.user.userpreference.preferred_categories.all()
                if preferences.exists():
                    queryset = queryset.filter(category__in=preferences).distinct()
                    messages.info(self.request, "Showing articles based on your preferences.")
                else:
                    messages.info(self.request, "No preferences set. Showing all articles.")
            except UserPreference.DoesNotExist:
                messages.info(self.request, "No preferences found. Showing all articles.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(article_count=Count('article'))
        context['current_category'] = self.request.GET.get('category', '')
        context['query'] = self.request.GET.get('q', '')
        context['recommendations'] = []

        if self.request.user.is_authenticated:
            try:
                user_preferences = self.request.user.userpreference.preferred_categories.all()
                logger.info(f"User preferences: {user_preferences}")

                if user_preferences.exists():
                    preferred_articles = Article.objects.filter(category__in=user_preferences)

                    read_article_ids = ReadingHistory.objects.filter(
                        user=self.request.user
                    ).values_list('article__id', flat=True)

                    recommendations = preferred_articles.exclude(
                        id__in=read_article_ids
                    ).order_by('-published_date')[:5]

                    context['recommendations'] = recommendations
                    logger.info(f"Recommendations: {recommendations}")
            except UserPreference.DoesNotExist:
                logger.warning("No UserPreference found for user.")

        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(user=self.request.user, article=obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        context['helpful_count'] = SummaryFeedback.objects.filter(article=article, is_helpful=True).count()
        context['not_helpful_count'] = SummaryFeedback.objects.filter(article=article, is_helpful=False).count()

        if self.request.user.is_authenticated:
            feedback = SummaryFeedback.objects.filter(user=self.request.user, article=article).first()
            context['user_feedback'] = feedback.is_helpful if feedback else None
        else:
            context['user_feedback'] = None

        return context


class HomePageView(TemplateView):
    template_name = 'news/homepage.html'


def landing_page(request):
    return render(request, 'landing.html')


@login_required
def reading_history(request):
    history = ReadingHistory.objects.filter(
        user=request.user
    ).select_related('article').order_by('-read_at')
    return render(request, 'news/reading_history.html', {'history': history})


@login_required
def generate_summary_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        try:
            num_sentences = int(request.POST.get('num_sentences', 5))
        except (TypeError, ValueError):
            num_sentences = 5

        num_sentences = max(1, min(num_sentences, 10))
        new_summary = generate_summary(article.content, article.title, num_sentences)
        article.summary = new_summary
        article.save()

        messages.success(request, f'Summary successfully generated with {num_sentences} sentence{"s" if num_sentences > 1 else ""}.')

    return redirect('article_detail', pk=pk)


@login_required
@require_POST
def submit_summary_feedback(request, pk):
    article = get_object_or_404(Article, pk=pk)
    is_helpful = request.POST.get('is_helpful')

    if is_helpful is not None:
        is_helpful_bool = (is_helpful.lower() == 'true')

        feedback, created = SummaryFeedback.objects.update_or_create(
            user=request.user,
            article=article,
            defaults={'is_helpful': is_helpful_bool}
        )

        messages.success(request, 'Thank you for your feedback!')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'helpful': is_helpful_bool})
        else:
            return redirect('article_detail', pk=pk)

    messages.error(request, 'Invalid feedback provided.')
    return redirect('article_detail', pk=pk)
from .utils import text_to_speech

def create_audio_for_article(article):
    if article.content:
        filename = f"article{article.id}.mp3"
        relative_audio_path = text_to_speech(article.content, filename)
        article.audio_file = relative_audio_path
        article.save()