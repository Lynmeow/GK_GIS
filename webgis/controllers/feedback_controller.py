from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from webgis.models.feedback import Feedback

def feedback_view(request):
    feedbacks = Feedback.objects.all()[:20]
    return render(request, 'webgis/feedback.html', {'feedbacks': feedbacks})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        Feedback.objects.create(
            user        = request.user,
            category    = request.POST.get('category', 'other'),
            title       = request.POST.get('title', ''),
            description = request.POST.get('description', ''),
            district    = request.POST.get('district', ''),
        )
        return redirect('feedback')
    return redirect('feedback')

def feedback_api(request):
    feedbacks = list(Feedback.objects.all()[:50].values(
        'id','category','title','description','district','status','created_at'
    ))
    for f in feedbacks:
        f['created_at'] = f['created_at'].strftime('%d/%m/%Y %H:%M')
    return JsonResponse({'success': True, 'feedbacks': feedbacks, 'total': len(feedbacks)})