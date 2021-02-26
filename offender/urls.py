from django.urls import path

from . import views

app_name = 'offender'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    #path('signup', views.Signup.as_view(), name="signup"),
    path('forgot-password', views.Forgot_password.as_view(), name='forgot_password'),
    path('logout', views.logout, name="logout"),
    path('recovery-password/<int:id>', views.Recovery_password.as_view(), name="recovery_password"),
    path('profile/<int:id>', views.Profile.as_view(), name="profile"),
    path('dashboard', views.Dashboard.as_view(), name='dashboard'),
    
    #-----our database urls -------#

    path('add-record', views.Add_record.as_view(), name='add_record'),
    path('view-record', views.View_record.as_view(), name='view_record'),
    path('record-detail/<int:id>', views.Record_detail.as_view(), name='record_detail'),
    #path('edit-record/<int:id>', views.Edit_record.as_view(), name='edit_record'),
    path('delete-record/<int:id>', views.Delete_record.as_view(), name='delete_record'),
    path('delete-experience/<int:id>', views.Delete_experience.as_view(), name='delete_experience'),
    path('change-block-status/<int:id>/',views.Change_block_status.as_view(),name='change_block_status'),
    path('block-record', views.Block_user_records.as_view(), name='block_record'),

    #------ NCDPS offender urls ------#

    path('offender-detail/', views.Offender_details.as_view(), name='offender_details'),
    path('delete-offender-experience/<int:id>', views.Delete_offender_experience.as_view(), name='delete_offender_experience'),
    path('change-offender-block-status/',views.Change_offender_block_status.as_view(),name='change_offender_block_status'),
    

    #------- MCSO inmate urls ------#
    path('inmate-detail/Inmate/Details/', views.Inmate_details.as_view(), name='innmate_details'),
    path('delete-inmate-experience/<int:id>', views.Delete_inmate_experience.as_view(), name='delete_inmate_experience'),
    path('change-inmate-block-status/',views.Change_inmate_block_status.as_view(),name='change_inmate_block_status'),
    
    
    

]