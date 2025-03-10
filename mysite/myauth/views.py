from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
)

from .models import Profile


class AboutMeView(UpdateView):
    model = Profile
    fields = ("avatar",)
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self):
        return self.request.user.profile


class UsersListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "users"
    template_name = "myauth/users_list.html"


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin,
                     UpdateView, DetailView):
    queryset = Profile.objects.select_related('user')
    fields = ['avatar', ]
    context_object_name = "profile"
    template_name = "myauth/user_details.html"

    def get_success_url(self):
        return reverse_lazy('myauth:user_details', kwargs={'pk': self.object.pk})

    def test_func(self):
        return (self.request.method not in ('POST', 'DELETE', 'UPDATE', 'PATCH')
                or self.request.user.is_staff
                or self.get_object().user.pk == self.request.user.pk)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class MyLogoutView(LogoutView, TemplateView):
    template_name = 'myauth/logout.html'
    http_method_names = ['get', 'post', 'delete']


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
