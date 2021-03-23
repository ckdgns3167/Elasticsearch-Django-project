from django.shortcuts import render


# Create your views here.

def main(request):
    return render(request, 'main.html')


def draw_chart(request):
    return render(request, 'draw_chart.html')
