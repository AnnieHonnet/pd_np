import pandas as pd
import numpy as np
from pathlib import Path



def pd_np():
    f_path = Path("/Users/nfs/annie/projects/pd_np/data/nba.csv")
    COL = ["Name","Team",  "Number", "Position","Age","Height", "Weight","College","Salary"]
    f = pd.read_csv(f_path, skip_blank_lines=True)
    f.set_index("Name",  inplace=True)
    #print(f)

#---------------------- df.LOC[] ------------------

    f2 = f.loc["Avery Bradley"]
   
#Team        Boston Celtics
# Number                 0.0
# Position                PG
# Age                   25.0
# Height                 6-2
# Weight               180.0
# College              Texas
# Salary           7730337.0
#Name: Avery Bradley, dtype: object



    f3 = f.loc[["Avery Bradley", "R.J. Hunter"]]  #----> has to have 2 diff rows to have a DATA FRAME  + DOUBLE Square Brackets
#                          Team  Number Position   Age Height  Weight        College     Salary
# Name                                                                                         
# Avery Bradley  Boston Celtics     0.0       PG  25.0    6-2   180.0          Texas  7730337.0
# R.J. Hunter    Boston Celtics    28.0       SG  22.0    6-5   185.0  Georgia State  1148640.0
    




    f4 = f.loc["Avery Bradley":"Isaiah Thomas"] #-------> print DATAFRAME containing rows specififc  + Cd
#                            Team  Number Position   Age Height  Weight            College      Salary
# Name                                                                                                
# Avery Bradley    Boston Celtics     0.0       PG  25.0    6-2   180.0              Texas   7730337.0
# Jae Crowder      Boston Celtics    99.0       SF  25.0    6-6   235.0          Marquette   6796117.0
# John Holland     Boston Celtics    30.0       SG  27.0    6-5   205.0  Boston University         NaN
# R.J. Hunter      Boston Celtics    28.0       SG  22.0    6-5   185.0      Georgia State   1148640.0
# Jonas Jerebko    Boston Celtics     8.0       PF  29.0   6-10   231.0                NaN   5000000.0
# Amir Johnson     Boston Celtics    90.0       PF  29.0    6-9   240.0                NaN  12000000.0
# Jordan Mickey    Boston Celtics    55.0       PF  21.0    6-8   235.0                LSU   1170960.0
# Kelly Olynyk     Boston Celtics    41.0        C  25.0    7-0   238.0            Gonzaga   2165160.0
# Terry Rozier     Boston Celtics    12.0       PG  22.0    6-2   190.0         Louisville   1824360.0
# Marcus Smart     Boston Celtics    36.0       PG  22.0    6-4   220.0     Oklahoma State   3431040.0
# Jared Sullinger  Boston Celtics     7.0        C  24.0    6-9   260.0         Ohio State   2569260.0
# Isaiah Thomas    Boston Celtics     4.0       PG  27.0    5-9   185.0         Washington   6912869.0



    
    
    f5= f.loc["Avery Bradley":"Isaiah Thomas", "College"] #-----------> print al rows indicated with specific column
# Name
# Avery Bradley                  Texas
# Jae Crowder                Marquette
# John Holland       Boston University
# R.J. Hunter            Georgia State
# Jonas Jerebko                    NaN
# Amir Johnson                     NaN
# Jordan Mickey                    LSU
# Kelly Olynyk                 Gonzaga
# Terry Rozier              Louisville
# Marcus Smart          Oklahoma State
# Jared Sullinger           Ohio State
# Isaiah Thomas             Washington

# ------------------ ------------------ ------------------
#                            df[]
#---------------------- ------------------ ------------------
    f6 = f["Team"]
# Avery Bradley    Boston Celtics
# Jae Crowder      Boston Celtics
# John Holland     Boston Celtics
# R.J. Hunter      Boston Celtics
# Jonas Jerebko    Boston Celtics
#                       ...      
# Shelvin Mack          Utah Jazz
# Raul Neto             Utah Jazz
# Tibor Pleiss          Utah Jazz
# Jeff Withey           Utah Jazz


    f7 = f[["Team", "Number"]]
#                          Team  Number
# Name                                 
# Avery Bradley  Boston Celtics     0.0
# Jae Crowder    Boston Celtics    99.0
# John Holland   Boston Celtics    30.0
# R.J. Hunter    Boston Celtics    28.0
# Jonas Jerebko  Boston Celtics     8.0
# ...                       ...     ...
# Shelvin Mack        Utah Jazz     8.0
# Raul Neto           Utah Jazz    25.0
# Tibor Pleiss        Utah Jazz    21.0
# Jeff Withey         Utah Jazz    24.0


    f["Experience"] = 1 #------------------> Add New Colum with value 1 
#                          Team  Number Position   Age Height  Weight            College     Salary  Experience
# Name                                                                                                         
# Avery Bradley  Boston Celtics     0.0       PG  25.0    6-2   180.0              Texas  7730337.0           1
# Jae Crowder    Boston Celtics    99.0       SF  25.0    6-6   235.0          Marquette  6796117.0           1
# John Holland   Boston Celtics    30.0       SG  27.0    6-5   205.0  Boston University        NaN           1
# R.J. Hunter    Boston Celtics    28.0       SG  22.0    6-5   185.0      Georgia State  1148640.0           1
# Jonas Jerebko  Boston Celtics     8.0       PF  29.0   6-10   231.0                NaN  5000000.0           1
    
    
    f = f.reset_index() #---------------> IMPORTANT to reset index before adding new row so the column stay consistent.
    new_row = pd.DataFrame({'Name' : ['Geeks'],
    'Team': ['Boston'],
    'Number': [3],
    'Position': ['PG'],
    'Age': [33],
    'Height': ['6-2'],
    'Weight': [189],
    'College': ['MIT'],
    'Salary': [99999], 
    'Experience' : [1]})
    f = pd.concat([f, new_row], ignore_index=True)
    

    f8 = f.loc[3] #---> 4th row. 
# Team        Boston Celtics
# Number                 0.0
# Position                PG
# Age                   25.0
# Height                 6-2
# Weight               180.0
# College              Texas
# Salary           7730337.0
# Name: Avery Bradley, dtype: object
# Name             R.J. Hunter
# Team          Boston Celtics
# Number                  28.0
# Position                  SG
# Age                     22.0
# Height                   6-5
# Weight                 185.0
# College        Georgia State
# Salary             1148640.0
# Experience                 1
# Name: 3, dtype: object


    f9 = f.iloc[3]
# Team        Boston Celtics
# Number                 0.0
# Position                PG
# Age                   25.0
# Height                 6-2
# Weight               180.0
# College              Texas
# Salary           7730337.0
# Name: Avery Bradley, dtype: object
# Name             R.J. Hunter
# Team          Boston Celtics
# Number                  28.0
# Position                  SG
# Age                     22.0
# Height                   6-5
# Weight                 185.0
# College        Georgia State
# Salary             1148640.0
# Experience                 1
# Name: 3, dtype: object


    #f8 == f9
# Name          True
# Team          True
# Number        True
# Position      True
# Age           True
# Height        True
# Weight        True
# College       True
# Salary        True
# Experience    True
# Name: 3, dtype: bool


    f10 = f[["Name", "Team","Age"]]  #------------> df[[]"Column1 Name", "Col2 Name", ...]]
    f11 = f.iloc[[1,2,3]]            #------------> df.iloc[[ index row 1, index row 2, ...]]
    f12 = f.loc[[1,2,3]] 
# f11 is            Name            Team  Number Position   Age Height  Weight            College     Salary  Experience
# 1   Jae Crowder  Boston Celtics    99.0       SF  25.0    6-6   235.0          Marquette  6796117.0           1
# 2  John Holland  Boston Celtics    30.0       SG  27.0    6-5   205.0  Boston University        NaN           1
# 3   R.J. Hunter  Boston Celtics    28.0       SG  22.0    6-5   185.0      Georgia State  1148640.0           1
# f12 is            Name            Team  Number Position   Age Height  Weight            College     Salary  Experience
# 1   Jae Crowder  Boston Celtics    99.0       SF  25.0    6-6   235.0          Marquette  6796117.0           1
# 2  John Holland  Boston Celtics    30.0       SG  27.0    6-5   205.0  Boston University        NaN           1
# 3   R.J. Hunter  Boston Celtics    28.0       SG  22.0    6-5   185.0      Georgia State  1148640.0           1


    f13 = f.loc[[3,4],["Name", "Team"]]
    f14 = f.iloc[[3,4],[0,1]]
    print(f13)
    print(f14)
    print(f13 == f14)




    data = pd.DataFrame({'Name': ['Geek1', 'Geek2', 'Geek3', 'Geek4', 'Geek5'],
                         'Age': [25, 30, 22, 35, 28], 'Salary': [50000, 60000, 45000, 70000, 55000]})
    data.set_index('Name', inplace=True)
#        Age  Salary
# Name              
# Geek1   25   50000
# Geek2   30   60000
# Geek3   22   45000
# Geek4   35   70000
# Geek5   28   55000

    row_0 = data.iloc[0,:] #------> Print rows by index 
# Age          25
# Salary    50000
# Name: Geek1, dtype: int64




pd_np()
        