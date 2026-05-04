from django.urls import path
from django.contrib.auth.decorators import login_required
from webgis.controllers import (
    home_controller, auth_controller, dashboard_controller,
    api_controller, analysis_controller, alert_controller,
    forecast_controller, report_controller, feedback_controller,
    admin_controller,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ── Public ──
    path('', home_controller.home, name='home'),
    path('stations/route/', home_controller.stations_route_view, name='stations_route'),
    path('api/stations/public/', api_controller.public_stations_api, name='api_stations_public'),
    path('login/', auth_controller.login_view, name='login'),
    path('logout/', auth_controller.logout_view, name='logout'),
   


    # API public
    path('api/weather/', api_controller.weather_api, name='api_weather'),
    path('api/districts/', api_controller.districts_api, name='api_districts'),
    path('api/gee/tile/', api_controller.gee_tile_api, name='api_gee_tile'),
    path('api/uhi/', api_controller.uhi_api, name='api_uhi'),
    path('api/water/', api_controller.water_api, name='api_water'),
    path('api/air/', api_controller.air_quality_api, name='api_air'),
    path('api/flood/districts/', api_controller.flood_district_api, name='api_flood_districts'),
    path('api/risk/', api_controller.risk_api, name='api_risk'),
    path('api/proposals/', api_controller.proposals_api, name='api_proposals'),
    path('api/proposals/review/', api_controller.review_proposal_api, name='api_proposals_review'),
    path('api/satellite/', api_controller.satellite_image_api, name='api_satellite'),

    # ── Researcher ──
    path('dashboard/', login_required(auth_controller.dashboard_view), name='dashboard'),
    path('map/', login_required(dashboard_controller.map_view), name='map'),

    path('analysis/', login_required(analysis_controller.analysis_view), name='analysis'),
    path('api/analysis/', login_required(analysis_controller.analysis_api), name='api_analysis'),
    path('api/analysis/monthly/', login_required(analysis_controller.analysis_monthly_api), name='api_analysis_monthly'),

    path('alert/', login_required(alert_controller.alert_view), name='alert'),
    path('api/alert/', login_required(alert_controller.alert_api), name='api_alert'),
    path('alert/create/', login_required(alert_controller.create_alert), name='create_alert'),
    path('alert/proposal/', login_required(alert_controller.submit_proposal), name='submit_proposal'),

    path('forecast/', login_required(forecast_controller.forecast_view), name='forecast'),
    path('api/forecast/', login_required(forecast_controller.forecast_api), name='api_forecast'),

    path('report/', login_required(report_controller.report_view), name='report'),
    path('api/report/', login_required(report_controller.report_api), name='api_report'),

    path('feedback/', login_required(feedback_controller.feedback_view), name='feedback'),
    path('api/feedback/', login_required(feedback_controller.feedback_api), name='api_feedback'),
    path('feedback/submit/', login_required(feedback_controller.submit_feedback), name='submit_feedback'),

    # ── Admin Panel ──
    path('admin-panel/', admin_controller.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', admin_controller.admin_users, name='admin_users'),
    path('admin-panel/users/create/', admin_controller.admin_user_create, name='admin_user_create'),
    path('admin-panel/users/<int:user_id>/edit/', admin_controller.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:user_id>/delete/', admin_controller.admin_user_delete, name='admin_user_delete'),
    path('admin-panel/stations/', admin_controller.admin_stations, name='admin_stations'),
    path('admin-panel/stations/create/', admin_controller.admin_station_create, name='admin_station_create'),
    path('admin-panel/stations/<int:station_id>/edit/', admin_controller.admin_station_edit, name='admin_station_edit'),
    path('admin-panel/stations/<int:station_id>/delete/', admin_controller.admin_station_delete, name='admin_station_delete'),
    path('admin-panel/proposals/', admin_controller.admin_proposals, name='admin_proposals'),
    path('admin-panel/proposals/<int:proposal_id>/review/', admin_controller.admin_proposal_review, name='admin_proposal_review'),
    path('api/admin/stations/', admin_controller.admin_stations_api, name='api_admin_stations'),
    path('admin-panel/audit-log/', admin_controller.admin_audit_log, name='admin_audit_log'),
    path('proposals/<int:pk>/revert/', admin_controller.admin_proposal_revert, name='admin_proposal_revert'),
    path('about/', admin_controller.about, name='about'),
    path('admin-panel/about/', admin_controller.admin_about_edit, name='admin_about_edit'),
    
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='webgis/auth/password_reset.html'
        ), 
        name='password_reset'),

    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='webgis/auth/password_reset_done.html'
        ), 
        name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='webgis/auth/password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),

    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='webgis/auth/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
]



LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'