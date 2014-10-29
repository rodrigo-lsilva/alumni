from django.conf.urls import patterns, include, url
from egressos.logica import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', views.main),
                       url(r'^home/$', views.home, name="home"),
                       url(r'^administracao/$', views.administracao, name="administracao"),
                       url(r'^personalizacao/$', views.personalizacao, name="personalizacao"),
                       url(r'^estatisticas/$', views.estatisticas, name="estatisticas"),
                       url(r'^graficoEgressosPorAno/$', views.graficoEgressosPorAno, name="graficoEgressosPorAno"),
                       url(r'^graficoEgressosVSRegistrados/$', views.graficoEgressosVSRegistrados, name="graficoEgressosVSRegistrados"),
                       url(r'^graficoEgressosVSRegistrados2/$', views.graficoEgressosVSRegistrados2, name="graficoEgressosVSRegistrados2"),
                       url(r'^consultas/$', views.executeQuery, name="consultas"),
                       url(r'^config/$', views.config, name="config"),
                       url(r'^edit/$', views.edit, name="edit"),
                       url(r'^multiple_invites/$', views.multipleinvite, name="multiple_invites"),
                       url(r'^search/$', views.search, name="search"),
                       url(r'^registrar/$', views.registrar, name="registrar"), # pagina de cadastro
                       url(r'^login/$', views.logar, name="logar"), # pagina de login
                       url(r'^logout/$', views.mylogout, name="logout"),
                       url(r'^profile/(?P<egresso_id>\d+)/$', views.profile, name="profile"),
                       url(r'^profileNotFound/(?P<registro_id>\d+)/$', views.profileNotFound, name="profileNotFound"),
                       url(r'^exist/(?P<egresso_id>\d+)/$', views.exist, name="exist"),
                       url(r'^user_invite/(?P<registro_id>\d+)/$', views.userinvite, name="user_invite"),
                       url(r'^wizard/(?P<registro_id>\d+)/(?P<key>.*)/$', views.wizard, name="wizard"),
                       url(r'^save/$', views.save, name="save"),
                       url(r'^invites/$', views.invites, name="invites"),
                       url(r'^class/$', views.myclass, name="class"),
                       url(r'^invite/(?P<key>.*)/$', views.invite, name="invite"),
                       url(r'^email/$', views.email, name="email"),
                       url(r'^email_save/$', views.emailsave, name="email_save"),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^changepasswd/', views.changepasswd, name="changepasswd"),
                       url(r'^favicon\.ico$', views.favicon, name="favicon"),
)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#urlpatterns = patterns('',

    # Examples:
    # url(r'^$', 'egressos.views.home', name='home'),
    # url(r'^egressos/', include('egressos.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

#)
