# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:54:43 2014
This routine can plot both the observed and modeled drifter tracks.
It has various options including how to specify start positions, how long to track, 
whether to generate animation output, etc. See Readme.
@author: Bingwei Ling
Derived from previous particle tracking work by Manning, Muse, Cui, Warren.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,clickmap, points_between, points_square,extend_units,totdis
from matplotlib import animation

st_run_time = datetime.now() # Caculate execution time with en_run_time
############################### Options #######################################
'''
Option 1: Drifter track.
Option 2: Specify the start point.
Option 3: Specify the start point with simulated map.
Option 4: Area(box) track.          
'''
######## Hard codes ##########
Option = 1 # 1,2,3,4
print 'Option %d'%Option
MODEL = 'GOM3'     # 'ROMS', 'GOM3','massbay','30yr'
GRIDS = ['GOM3','massbay','30yr']    # All belong to FVCOM. '30yr' works from 1977/12/31 22:58 to 2014/1/1 0:0
depth = 1    # depth below ocean surface, positive
track_days = 2    #MODEL track time(days)
track_way = 'forward'    # Three options: backward, forward and both. 'both' only apply to Option 2 and 3.
image_style = 'plot'      # Two option: 'plot', animation
# You can track form now by specify start_time = datetime.now(pytz.UTC) 
#start_time = datetime(2015,11,1,0,0,0)#datetime.now(pytz.UTC) 
start_time = datetime.utcnow()
end_time = start_time + timedelta(track_days)
model_boundary_switch = 'OFF' # OFF or ON. Only apply to FVCOM
streamline = 'ON'
save_dir = './Results/'
colors = ['magenta','green','olive','orange','blue','yellow','red']
utcti = datetime.utcnow(); utct = utcti.strftime('%H')
locti = datetime.now(); loct = locti.strftime('%H')
ditnu = int(utct)-int(loct) # the deference between UTC and local time .
if ditnu < 0:
    ditnu = int(utct)+24-int(loct)
locstart_time = start_time - timedelta(hours=ditnu)

################################## Option ####################################

drifter_ID = ['1504107017','1504107022','150410705','1504107023']
# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"
INPUT_DATA = 'drift_X.dat'#'drift_jml_2015_1.dat'      


addpointway = 'square'  #Two options: random, square
if addpointway=='random':
    num = 33
    st_lat = np.random.uniform(41.9,42.1,num)[:]
    st_lon = np.random.uniform(-70.4,-70.6,num)[:]
if addpointway=='square':
    centerpoint = (41.9,-70.26); unit = 0.04; number = 3
    (st_lat,st_lon) = extend_units(centerpoint,unit,number)

############################## Common codes ###################################
loop_length = []
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
points = {'lats':[],'lons':[]}  # collect all points we've gained

############################## Option 1 ###################################

dstart_time = datetime.utcnow()-timedelta(track_days) #datetime(2015,1,24,0,0,0,0,pytz.UTC)

dft_num = len(drifter_ID)
dlon_set = [[]]*dft_num; dlat_set = [[]]*dft_num; dtime = [[]]*dft_num
mlon_set = [[]]*dft_num; mlat_set = [[]]*dft_num; mtime = [[]]*dft_num

for i in range(dft_num): 
    print "NO.%d,ID: %s"%(i+1,drifter_ID[i])
    drifter = get_drifter(drifter_ID[i], INPUT_DATA)
    try:
        dr_points = drifter.get_track(dstart_time,track_days)
    except:
        print drifter_ID[i]+'is unavailable.'
    else:
        dlon_set[i]=dr_points['lon']; dlat_set[i]=dr_points['lat']; dtime[i]=dr_points['time']
        print 'Drifter points: ',len(dlon_set[i])
        mstart_time = dr_points['time'][-1]
        check_drifter = start_time-mstart_time
        if check_drifter.seconds > 10800: # 3*3600
            mlon_set[i]=dlon_set[i]; mlat_set[i]=dlat_set[i]; mtime[i]=dtime[i]
            continue
        #mend_time = dr_points['time'][-1] + timedelta(track_days)
        
        if track_way=='backward':
            end_time = mstart_time 
            mstart_time = end_time - timedelta(track_days)  #''' 
            
        if MODEL in GRIDS:
            get_obj =  get_fvcom(MODEL)
            print dr_points['time'][-1]
            url_fvcom = get_obj.get_url(mstart_time,end_time)
            b_points = get_obj.get_data(url_fvcom) # b_points is model boundary points.
            point,num = get_obj.get_track(dr_points['lon'][-1],dr_points['lat'][-1],depth,track_way)
            
        if MODEL=='ROMS':        
            get_obj = get_roms()
            url_roms = get_obj.get_url(mstart_time,end_time)
            get_obj.get_data(url_roms)
            point = get_obj.get_track(dr_points['lon'][-1],dr_points['lat'][-1],depth,track_way)#,DEPTH
            if len(point['lon'])==1:
                print 'Start point on the land or out of Model area.'
                sys.exit('Invalid point')
                
        mlon_set[i]=point['lon']; mlat_set[i]=point['lat'];mtime[i]=point['time']
        
        points['lats'].extend(point['lat']); points['lons'].extend(point['lon'])
        points['lats'].extend(dr_points['lat']); points['lons'].extend(dr_points['lon'])
        
image_style = 'animation'
hitland = 0; onland = 0
stp_num = len(st_lat)
lon_set = [[]]*stp_num; lat_set = [[]]*stp_num; smtimes = [[]]*stp_num
print 'You added %d points.' % stp_num,st_lon,st_lat

#start_time = datetime.now(pytz.UTC)+timedelta(track_time)  #datetime(2015,2,10,12,0,0,0,pytz.UTC)#
#end_time = start_time + timedelta(track_days)
if track_way=='backward':
    end_time = start_time 
    start_time = end_time - timedelta(track_days)  #'''
print 'Start time(UTC): ',start_time
print 'End time(UTC): ',end_time 
if MODEL in GRIDS:            
    get_obj = get_fvcom(MODEL)
    url_fvcom = get_obj.get_url(start_time,end_time)
    b_points = get_obj.get_data(url_fvcom)# b_points is model boundary points.        
    
    for i in range(stp_num):
        print 'Running the %dth of %d drifters.'%(i+1,stp_num)
        point,nu = get_obj.get_track(st_lon[i],st_lat[i],depth,track_way)
        #point,nu = get_obj.get_track(st_lon[i],st_lat[i],lonc,latc,u,v,b_points,track_way)
        lon_set[i] = point['lon']; lat_set[i] = point['lat']; smtimes[i] = point['time']
        loop_length.append(len(point['lon']))
        if nu==0:
            onland+=1
        if nu==1:
            hitland+=1             
    
    for i in smtimes:
        if len(i)==max(loop_length):
            smtime = i
            break
    #smtime = [i for i in smtimes if len(i)==max(loop_length) break] # streamline model time .
    p = float(hitland)/float(stp_num-onland)*100
    print "%d points, %d hits the land, ashore percent is %.f%%."%(stp_num-onland,hitland,int(round(p)))
    #np.savez('model_points.npz',lon=lon_set,lat=lat_set)
for i in range(stp_num):
    points['lons'].extend(lon_set[i])
    points['lats'].extend(lat_set[i])

######################### 4 Features Option #############################
if model_boundary_switch=='ON':
    po = b_points.T
    ax.plot(po[0],po[1],'bo',markersize=3)
if streamline == 'ON':
    lonpps,latpps,US,VS,speeds = get_obj.streamlinedata(points,depth,track_way)
    #np.savez('streamline.npz',lonpps=lonpps,latpps=latpps,US=US,VS=VS,speeds=speeds)

######################### Plot #######################################       

#colors=uniquecolors(stp_num) #config colors

if streamline == 'ON':
    def animate(n): #del ax.collections[:]; del ax.lines[:]; ;
        ax.cla()  
        if track_way=='backward':
            Time = (locstart_time-timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
        else:
            Time = (locstart_time+timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
        plt.suptitle('%.f%% simulated drifters ashore\n%d days, %d m, %s'%(int(round(p)),track_days,depth,Time))
        
        plt.streamplot(lonpps[n],latpps[n],US[n],VS[n], color=speeds[n],arrowsize=4,cmap=plt.cm.cool,density=2.0)
        
        for i in range(dft_num):
            ax.plot(dlon_set[i],dlat_set[i],'-',color=colors[i%7],linewidth=2,label=drifter_ID[i][-5:])
            
        for j in xrange(stp_num):
            ax.plot(lon_set[j][0],lat_set[j][0],color='k',marker='x',markersize=3)#colors[j%10]
            if n>=len(lon_set[j]):
                ax.plot(lon_set[j][-1],lat_set[j][-1],'o',color='black',markersize=5)
            if n<len(lon_set[j]):
                if n<5:                
                    ax.plot(lon_set[j][:n+1],lat_set[j][:n+1],'o-',color='black',markersize=3)#,label='Depth=10m'            
                if n>=5:
                    ax.plot(lon_set[j][n-4:n+1],lat_set[j][n-4:n+1],'o-',color='black',markersize=3)
        
        for i in range(dft_num):
            if smtime[n] > mtime[i][-1]:
                #ax.plot(dlon_set[i],dlat_set[i],'-',color=colors[i%7],linewidth=2,label=drifter_ID[i][-5:])
                ax.plot(mlon_set[i][-1],mlat_set[i][-1],'o',color=colors[i%7],markersize=5)
            if smtime[n] in mtime[i]:
                mti = mtime[i].index(smtime[n])
                '''ax.annotate(drifter_ID[i],xy=(dlon_set[i][-1],dlat_set[i][-1]),xytext=(dlon_set[i][-1]+0.01*track_days,
                            dlat_set[i][-1]+0.01*track_days),fontsize=6,arrowprops=dict(arrowstyle="fancy")) #'''
                #ax.plot(dlon_set[i],dlat_set[i],'-',color=colors[i%7],linewidth=2,label=drifter_ID[i][-5:]) # ,markersize=6, linewidth = 4
                if mti<5:
                    ax.plot(mlon_set[i][:mti+1],mlat_set[i][:mti+1],'o-',color=colors[i%7],markersize=4) #,label='Model'
                if mti>=5:
                    ax.plot(mlon_set[i][mti-4:mti+1],mlat_set[i][mti-4:mti+1],'o-',color=colors[i%7],markersize=4) #,label='Model'
        draw_basemap(ax, points)  # points is using here
        #plt.legend(loc=3,prop={'size':5})
        
    anim = animation.FuncAnimation(fig, animate, frames=max(loop_length), interval=1000) #        
    plt.clim(vmin=0, vmax=2)
    plt.colorbar()
else:
    draw_basemap(ax, points)  # points is using here
    def animate(n): #del ax.collections[:]; del ax.lines[:]; ax.cla(); ax.lines.remove(line)        
        if track_way=='backward':
            Time = (locstart_time-timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
        else:
            Time = (locstart_time+timedelta(hours=n)).strftime("%d-%b-%Y %H:%M")
        plt.suptitle('%.f%% simulated drifters ashore\n%d days, %d m, %s'%(int(round(p)),track_days,depth,Time))
        del ax.lines[:]        
        for j in xrange(stp_num):
            ax.plot(lon_set[j][0],lat_set[j][0],color=colors[j%10],marker='x',markersize=4)
            if n>=len(lon_set[j]):
                ax.plot(lon_set[j][-1],lat_set[j][-1],'o',color=colors[j%10],markersize=5)
            if n<5:                
                if n<len(lon_set[j]):
                    ax.plot(lon_set[j][:n+1],lat_set[j][:n+1],'o-',color=colors[j%10],markersize=4)#,label='Depth=10m'            
            if n>=5:
                if n<len(lon_set[j]):
                    ax.plot(lon_set[j][n-4:n+1],lat_set[j][n-4:n+1],'o-',color=colors[j%10],markersize=4)
    anim = animation.FuncAnimation(fig, animate, frames=max(loop_length),interval=500) #, 
    
##################################### The End ##########################################
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' running the code. End at '+str(en_run_time)
### Save #########
#plt.legend(loc=3)
'''if image_style=='plot':
    plt.savefig(save_dir+'%s-%s_%s'%(MODEL,track_way,en_run_time.strftime("%d-%b-%Y_%H:%M")),dpi=400,bbox_inches='tight')#'''
if image_style=='animation':#ffmpeg,imagemagick,mencoder fps=20'''
    anim.save(save_dir+'%s-%s_%s.gif'%(MODEL,track_way,en_run_time.strftime("%d-%b-%Y_%H:%M")),writer='imagemagick',dpi=250) #,,,fps=1'''
#plt.show()
