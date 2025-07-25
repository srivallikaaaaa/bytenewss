from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from .models import Article, Category
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import DetailView
from .models import Article, ReadingHistory  # Make sure ReadingHistory is imported

from django.contrib import messages
from .models import Article
from news.models import UserPreference 

from django.contrib.auth.decorators import login_required
from .utils import generate_summary


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from news.utils import summarize_text

 # ensure this is imported


# news/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from news.models import ReadingHistory
import logging
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

        # ✅ Filter by category if provided
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        # ✅ Apply search filter
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
        # Personalized filtering based on user preferences


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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


class HomePageView(TemplateView):
    template_name = 'news/homepage.html'


def landing_page(request):
    return render(request, 'website/landing.html')


@login_required
def reading_history(request):
    history = ReadingHistory.objects.filter(
        user=request.user
    ).select_related('article').order_by('-read_at')
    return render(request, 'news/reading_history.html', {'history': history})

@login_required
def generate_summary_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.summary = generate_summary(article.content, article.title)
    article.save()
    messages.success(request, "Summary re-generated successfully!")
    return redirect('news:detail', pk=pk)

@login_required
@require_POST
def submit_summary_feedback(request, pk):
    article = get_object_or_404(Article, pk=pk)
    is_helpful = request.POST.get('is_helpful')
    if is_helpful is not None:
        is_helpful_bool = (is_helpful.lower() == 'true')
        SummaryFeedback.objects.update_or_create(
            user=request.user,
            article=article,
            defaults={'is_helpful': is_helpful_bool}
        )
        messages.success(request, 'Thank you for your feedback!')
    else:
        messages.error(request, 'Invalid feedback provided.')
    return redirect('news:detail', pk=pk)


def summarize_example(request):
    text = """
    India won the match against Australia in a thrilling finish. 
    The crowd was ecstatic as Virat Kohli hit the winning runs. 
    Earlier, Australia had set a target of 250 runs. 
    India chased the total in the final over. 
    The match was held in Mumbai.
    """
    summary = summarize_text(text, num_sentences=2)
    return JsonResponse({'summary': summary})