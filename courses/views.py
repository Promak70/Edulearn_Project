from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .forms import  LessonForm, CourseForm
from .forms import CourseEnrollmentForm
from .models import Student
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . forms import UserUpdateForm
from django.views.generic import ListView, DetailView
from .models import Course, Lesson
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Lesson
from .serializers import CourseSerializer

# def home(request):
#       courses = Course.objects.all()
#       return render(request, 'courses/index.html', {'allCourses': courses})


class CourseListView(ListView):
   model = Course
   template_name = 'courses/course_list.html'
   context_object_name = 'courses'

# class CourseDetailView(DetailView):
#    model = Course
#    template_name = 'courses/course_detail.html'
#    context_object_name = 'course'

#    def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Adding lessons to the context
#         context['lessons'] = self.object.lessons.all()
#         return context

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})


class CourseCreateView(CreateView):
   model = Course
   fields = ['title', 'description', 'duration', 'thumbnail']
   template_name = 'courses/course_form.html'
   success_url = reverse_lazy('course_list')

   def form_valid(self, form):
        # Add a success message when the form is valid
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)
   
   def form_invalid(self, form):
        # Add an error message when the form is invalid
        messages.error(self.request, "There was an error creating the course. Please check the form and try again.")
        return super().form_invalid(form)
   
class CourseListAPI(APIView):
  def get(self, request):
   courses = Course.objects.all()
   serializer = CourseSerializer(courses, many=True)
   return Response(serializer.data)

class CourseDetailAPI(APIView):
   def get(self, request, pk):
     try:
        course = Course.objects.get(pk=pk)
     except Course.DoesNotExist:
       return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
     serializer = CourseSerializer(course)
     return Response(serializer.data)

class EnrollStudentAPI(APIView):
   def post(self, request):
    student_email = request.data.get('email')
    course_id = request.data.get('course_id')

    try:
       course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
      return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    student, created = Student.objects.get_or_create(email=student_email)
    student.enrolled_courses.add(course)

    return Response({'message': f'{student.email} has been enrolled in {course.title}'})    
  # Enrolled Students
 
def enrolled_students(request, course_id):
     course = get_object_or_404(Course, id=course_id)
     students = course.students.all()
     return render(request, 'courses/enrolled_students.html', {'course': course, 'students': students})
# # Update Course
def course_update(request, course_id):
      course = get_object_or_404(Course, id=course_id)
      if request.method == "POST":
          form = CourseForm(request.POST, request.FILES, instance=course)
          if form.is_valid():
             form.save()
             messages.success(request, "Course updated successfully!")
             return redirect('course_list')
      else:
         form = CourseForm(instance=course)
    
      return render(request, 'courses/course_form.html', {'form': form})

# # Delete Course
def course_delete(request, course_id):
      course = get_object_or_404(Course, id=course_id)
      if request.method == "POST":
          course.delete()
          messages.success(request, "Course deleted successfully!")
          return redirect('course_list')

      return render(request, 'courses/course_confirm_delete.html', {'course': course})

# # Create Lesson
def lesson_create(request):
      if request.method == "POST":
          form = LessonForm(request.POST)
          if form.is_valid():
             form.save()
             messages.success(request, "Lesson created successfully!")
             return redirect('course_list')
      else:
          form = LessonForm()
    
      return render(request, 'courses/lesson_form.html', {'form': form})

# # Update Lesson
def lesson_update(request, lesson_id):
      lesson = get_object_or_404(Lesson, id=lesson_id)
      if request.method == "POST":
          form = LessonForm(request.POST, instance=lesson)
          if form.is_valid():
              form.save()
              messages.success(request, "Lesson updated successfully!")
              return redirect('course_list')
      else:
          form = LessonForm(instance=lesson)
    
      return render(request, 'courses/lesson_form.html', {'form': form})

# # Delete Lesson
def lesson_delete(request, lesson_id):
      lesson = get_object_or_404(Lesson, id=lesson_id)
      if request.method == "POST":
          lesson.delete()
          messages.success(request, "Lesson deleted successfully!")
          return redirect('course_list')

      return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})
 
import logging

logger = logging.getLogger(__name__)

def enroll_student(request):
    

      if request.method == 'POST':
          form = CourseEnrollmentForm(request.POST)
          if form.is_valid():
              student_name = form.cleaned_data['student_name']
              student_email = form.cleaned_data['student_email']
              course = form.cleaned_data['course']
              student, created = Student.objects.get_or_create(email=student_email)
              student.name = student_name  # Save the name if not already set
              student.save()
              if course in student.enrolled_courses.all():
                  messages.error(request, "You are already enrolled in this course.")
                  return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
              else:
                  messages.success(request, "You have been enrolled successfully!")
                  student.enrolled_courses.add(course)

              logger.info(f"Student enrolled: {student_email} in course: {course.title}")
              return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
          elif messages.get_messages(request):
              return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course, 'messages': messages.get_messages(request)})


          else:
              logger.error("Form is not valid.")
              logger.error(form.errors)

      form = CourseEnrollmentForm()
      return render(request, 'courses/enroll_student.html', {'form': form})

def view_students(request, course_id):
      course = get_object_or_404(Course, id=course_id)
      students = course.students.all()
      return render(request, 'courses/view_students.html', {
          'course': course,
          'students': students,
      })
def register(request):
    if request.method == 'POST':

       form = UserCreationForm(request.POST)
       if form.is_valid():
          user = form.save()
          login(request, user)
          messages.success(request, "Registration successful!")
          return redirect('/')
    else:
      form = UserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

def user_login(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)
      if form.is_valid():
         user = form.get_user()
         login(request, user)
         messages.success(request, "Login successful!")
         return redirect('/')
      else:
         messages.error(request, "Invalid username or password.")
   else:
     form = AuthenticationForm()
   return render(request, 'courses/login.html', {'form': form})
@login_required
def user_logout(request):
   logout(request)
   messages.success(request, "You have been logged out.")
   return redirect('/')


@login_required
def profile(request):
    if request. method == 'POST':
       form = UserUpdateForm(request. POST, instance = request. user)
       if form. is_valid():
          form. save()
          messages. success(request,"Profile updated successfully!")
          return redirect('profile')
    else:
      form = UserUpdateForm(instance = request. user)
    return render(request, 'courses/profile.html',{'form': form})


# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Course, Lesson
# from .forms import CourseForm, LessonForm
# from .forms import CourseEnrollmentForm
# from .models import Student
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib import messages
# from . forms import UserUpdateForm

# # Home Page
# def home(request):
#     courses = Course.objects.all()
#     return render(request, 'courses/index.html', {'allCourses': courses})

# # Welcome Page
# def welcome(request):
#     return render(request, "courses/description.html")

# # Course Details
# def course_details(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.all()
#     return render(request, 'courses/course_list.html', {'lessons': lessons, 'course': course})
# # Enrolled Students
# def enrolled_students(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     students = course.students.all()
#     return render(request, 'courses/enrolled_students.html', {'course': course, 'students': students})
# # Course List
# @login_required
# def course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'courses/course_list.html', {'courses': courses})

# # Course Detail
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.all()
#     return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})

# # Create Course
# def course_create(request):
#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course created successfully!")
#             return redirect('course_list')
#     else:
#         form = CourseForm()
    
#     return render(request, 'courses/course_form.html', {'form': form})

# # Update Course
  # def course_update(request, course_id):
  #     course = get_object_or_404(Course, id=course_id)
  #     if request.method == "POST":
  #         form = CourseForm(request.POST, request.FILES, instance=course)
  #         if form.is_valid():
  #            form.save()
  #            messages.success(request, "Course updated successfully!")
  #            return redirect('course_list')
  #     else:
  #        form = CourseForm(instance=course)
    
  #     return render(request, 'courses/course_form.html', {'form': form})

# # Delete Course
  # def course_delete(request, course_id):
  #     course = get_object_or_404(Course, id=course_id)
  #     if request.method == "POST":
  #         course.delete()
  #         messages.success(request, "Course deleted successfully!")
  #         return redirect('course_list')

  #     return render(request, 'courses/course_confirm_delete.html', {'course': course})

# # Create Lesson
#   def lesson_create(request):
#       if request.method == "POST":
#           form = LessonForm(request.POST)
#           if form.is_valid():
#              form.save()
#              messages.success(request, "Lesson created successfully!")
#              return redirect('course_list')
#       else:
#           form = LessonForm()
    
#       return render(request, 'courses/lesson_form.html', {'form': form})

# # # Update Lesson
#   def lesson_update(request, lesson_id):
#       lesson = get_object_or_404(Lesson, id=lesson_id)
#       if request.method == "POST":
#           form = LessonForm(request.POST, instance=lesson)
#           if form.is_valid():
#               form.save()
#               messages.success(request, "Lesson updated successfully!")
#               return redirect('course_list')
#       else:
#           form = LessonForm(instance=lesson)
    
#       return render(request, 'courses/lesson_form.html', {'form': form})

# # # Delete Lesson
#   def lesson_delete(request, lesson_id):
#       lesson = get_object_or_404(Lesson, id=lesson_id)
#       if request.method == "POST":
#           lesson.delete()
#           messages.success(request, "Lesson deleted successfully!")
#           return redirect('course_list')

#       return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})
 
# import logging

# logger = logging.getLogger(__name__)
#   def enroll_student(request):
    

#       if request.method == 'POST':
#           form = CourseEnrollmentForm(request.POST)
#           if form.is_valid():
#               student_name = form.cleaned_data['student_name']
#               student_email = form.cleaned_data['student_email']
#               course = form.cleaned_data['course']
#               student, created = Student.objects.get_or_create(email=student_email)
#               student.name = student_name  # Save the name if not already set
#               student.save()
#               if course in student.enrolled_courses.all():
#                   messages.error(request, "You are already enrolled in this course.")
#                   return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
#               else:
#                   messages.success(request, "You have been enrolled successfully!")
#                   student.enrolled_courses.add(course)

#               logger.info(f"Student enrolled: {student_email} in course: {course.title}")
#               return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
#           elif messages.get_messages(request):
#               return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course, 'messages': messages.get_messages(request)})


#           else:
#               logger.error("Form is not valid.")
#               logger.error(form.errors)

#       form = CourseEnrollmentForm()
#       return render(request, 'courses/enroll_student.html', {'form': form})

#   def view_students(request, course_id):
#       course = get_object_or_404(Course, id=course_id)
#       students = course.students.all()
#       return render(request, 'courses/view_students.html', {
#           'course': course,
#           'students': students,
#       })
#   def register(request):
#     if request.method == 'POST':

#        form = UserCreationForm(request.POST)
#        if form.is_valid():
#           user = form.save()
#           login(request, user)
#           messages.success(request, "Registration successful!")
#           return redirect('/')
#     else:
#       form = UserCreationForm()
#     return render(request, 'courses/register.html', {'form': form})

#   def user_login(request):
#    if request.method == 'POST':
#       form = AuthenticationForm(data=request.POST)
#       if form.is_valid():
#          user = form.get_user()
#          login(request, user)
#          messages.success(request, "Login successful!")
#          return redirect('/')
#       else:
#          messages.error(request, "Invalid username or password.")
#    else:
#      form = AuthenticationForm()
#    return render(request, 'courses/login.html', {'form': form})

#   def user_logout(request):
#    logout(request)
#    messages.success(request, "You have been logged out.")
#    return redirect('/')

# # # @login_required
# # # def course_list(request):
# # #   courses = Course. objects. all()
# # #   return render(request, 'courses/course_list.html',{'course': courses})

#   @login_required
#   def profile(request):
#     if request. method == 'POST':
#        form = UserUpdateForm(request. POST, instance = request. user)
#        if form. is_valid():
#           form. save()
#           messages. success(request,"Profile updated successfully!")
#           return redirect('profile')
#     else:
#       form = UserUpdateForm(instance = request. user)
    # return render(request, 'courses/profile.html',{'form': form})
    