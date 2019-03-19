import json
import shutil

def QDMCheck(name):
    '''
    This checks if we need to QDM.
    Arguments:
    name - name of something
    '''
    return 0

if __name__ == "__main__":
    with open('./receive/[groundstation].json') as f:
        datain = json.load(f)
        
    QDM = datain['QDM']
    CDM = datain['CDM']
    STAB = datain['Stabilization']
    CRASH = datain['Crash']
    IGNITION = datain['Ignition']
    DROGUE = datain['Drogue']
    MAIN_CHUTE = datain['Main_Chute']

    if QDM == 0:
        data = {}
        data['QDM initiated'] = []
        with open('./QDM/initiated.json','w') as outfile:
            json.dump(data, outfile)

    shutil.move('./receive/[groundstation].json','./archive')




