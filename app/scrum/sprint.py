# -*- coding: utf-8 -*-

from flask import request, session, Blueprint, json
from app.scrum.sprintClass       import *
from app.scrum.backLog           import *
from app.scrum.userHistory       import *
from app.scrum.task              import *
sprint = Blueprint('sprint', __name__)

@sprint.route('/sprint/ACrearSprint', methods=['POST'])
def ACrearSprint():
    #POST/PUT parameters
    params   = request.get_json()
    results = [{'label':'/VSprints', 'msg':['Sprint creado']}, {'label':'/VCrearSprint', 'msg':['Error al crear Sprint']}, ]
    res     = results[1]

    # Obtenemos el id del producto
    idPila  = int(session['idPila'])

    if request.method == 'POST':
        # Extraemos los parámetros
        newNumero      = params['numero'] 
        newDescription = params['descripcion']
        
        oSprint = sprints()
        result  = oSprint.insertSprint(newNumero, newDescription, idPila)

        if result:
            res = results[0]

    res['label'] = res['label'] + '/' + str(idPila)

    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']
    return json.dumps(res)



@sprint.route('/sprint/AElimSprint')
def AElimSprint():
    #POST/PUT parameters
    params  = request.get_json()
    results = [{'label':'/VSprints', 'msg':['Sprint eliminado']}, {'label':'/VSprint', 'msg':['Error al eliminar Sptrint']}, ]
    res     = results[1]
    
    # Obtenemos el id del producto
    idPila       = int(session['idPila'])

    # Obtenemos el id del sprint
    #idSprint = int(params['idSprint'])
    idSprint = int(session['idSprint'])

    # Conseguimos el sprint a eliminar
    oSprint  = sprints()
    found    = oSprint.searchIdSprint(idSprint,idPila)

    if (found != []):
        deleted = oSprint.deleteSprint(found[0].S_numero, found[0].S_idBacklog)

    if deleted:
            res = results[0]  

    res['label'] = res['label'] + '/' + str(idSprint)

    #Action code ends here
    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']
    return json.dumps(res)

@sprint.route('/sprint/AElimSprintHistoria')
def AElimSprintHistoria():
    #POST/PUT parameters
    params = request.get_json()
    results = [{'label':'/VSprint', 'msg':['Historia Eliminado']}, {'label':'/VSprint', 'msg':['Error al eliminar historia']}, ]
    res = results[1]

    idSprint = int(session['idSprint'])
    idPila = int(session['idPila'])
    idHistoriaEliminar = int(request.args['id'])

    oSprint  = sprints()
    oUserHistory = userHistory()
    oTask = task()
    deletedHistoryID=[]
    if oSprint.deleteAssignedSprintHistory(idSprint,idPila,idHistoriaEliminar):
        # Chequeamos si es epica, si lo es eliminamos sus hijos
        deletedHistoryID.append(idHistoriaEliminar)
        if oUserHistory.isEpic(idHistoriaEliminar):
            for idHistoria in oUserHistory.historySuccesors(idHistoriaEliminar):
                oSprint.deleteAssignedSprintHistory(idSprint,idPila, idHistoria)
                deletedHistoryID.append(idHistoria)

        # Eliminamos sus tareas
        for idHistoria in deletedHistoryID:
            tareas = oTask.taskAsociatedToUserHistory(idHistoria)
            for tarea in tareas:
                oSprint.deleteAssignedSprintTask(idSprint, idPila, tarea.HW_idTask)

        res = results[0]

    res['label'] = res['label'] + '/' + str(idSprint)

    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']

    return json.dumps(res)


@sprint.route('/sprint/AElimSprintTarea')
def AElimSprintTarea():
    #POST/PUT parameters
    params = request.get_json()
    results = [{'label':'/VSprint', 'msg':['Tarea eliminada']}, {'label':'/VSprint', 'msg':['Error al eliminar tarea']}, ]
    res = results[1]
    #Action code goes here, res should be a list with a label and a message

    idSprint = int(session['idSprint'])
    idPila = int(session['idPila'])
    idTareaEliminar = int(request.args['id'])

    oSprint  = sprints()
    if oSprint.deleteAssignedSprintTask(idSprint,idPila,idTareaEliminar):
        res = results[0]

    res['label'] = res['label'] + '/' + str(idSprint)

    #Action code ends here
    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']
    return json.dumps(res)

@sprint.route('/sprint/AModifSprint', methods=['POST'])
def AModifSprint():
    #POST/PUT parameters
    params = request.get_json()

    results = [{'label':'/VSprints', 'msg':['Sprint modificado']}, {'label':'/VSprints', 'msg':['Error al guardar Sprint']}, ]
    res = results[0]

    idPila   = int(session['idPila'])
    idSprint = int(session['idSprint'])
    newSprintNumber = int(params['numero'])
    newDescription  = str(params['descripcion'])

    res['label'] = res['label'] + '/' + str(idPila)
    oSprint = sprints()
    result  = oSprint.updateSprint(idSprint, idPila, newSprintNumber, newDescription)
    
    if not result:
        res = results[1]        
        res['label'] = res['label'] + '/' + str(idPila)

    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']

    res['idPila'] = idPila


    return json.dumps(res)

@sprint.route('/sprint/ASprintHistoria', methods=['POST'])
def ASprintHistoria():
    #POST/PUT parameters
    params = request.get_json()
    results = [{'label':'/VSprint', 'msg':['Historia Asignado']}, {'label':'/VSprint', 'msg':['Error al Asignar Historia']}, ]
    res = results[1]
    #Action code goes here, res should be a list with a label and a message

    idSprint = int(params['idSprint'])
    idPila = params['idPila']
    idHistoria = params['historia']

    oSprint = sprints()
    oUserHistory = userHistory()
    if oSprint.asignSprintHistory(idSprint,idPila, idHistoria):
        # Chequeamos si es epica, si lo es agregamos las sub-historias
        if oUserHistory.isEpic(idHistoria):
            for idHistoria in oUserHistory.historySuccesors(idHistoria):
                oSprint.asignSprintHistory(idSprint,idPila, idHistoria)

        res = results[0]

    res['label'] = res['label'] + '/' + str(idSprint)
    #Action code ends here
    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']
    return json.dumps(res)


@sprint.route('/sprint/ASprintTarea', methods=['POST'])
def ASprintTarea():
    #POST/PUT parameters
    params = request.get_json()
    results = [{'label':'/VSprint', 'msg':['Tarea asignada']}, {'label':'/VSprint', 'msg':['Error al asignar tarea']}, ]
    res = results[1]
    #Action code goes here, res should be a list with a label and a message

    idSprint = int(params['idSprint'])
    idPila = params['idPila']
    idTarea = params['tarea']

    oSprint = sprints()
    if oSprint.asignSprintTask(idSprint,idPila, idTarea):
        res = results[0]

    res['label'] = res['label'] + '/' + str(idSprint)
    #Action code ends here
    if "actor" in res:
        if res['actor'] is None:
            session.pop("actor", None)
        else:
            session['actor'] = res['actor']
    return json.dumps(res)

@sprint.route('/sprint/VCrearSprint')
def VCrearSprint():
    #GET parameter
    res = {}

    idPila = request.args.get('idPila',1)
        
    if "actor" in session:
        res['actor']=session['actor']

    if 'usuario' not in session:
      res['logout'] = '/'
      return json.dumps(res)

    res['fSprint'] = {'idPila':idPila}
    res['usuario'] = session['usuario']
    res['idPila']  = idPila

    return json.dumps(res)



@sprint.route('/sprint/VSprint')
def VSprint():
    #GET parameter
    res = {}

    # Obtenemos el id del producto y del sprint
    idPila   = int(session['idPila'])
    idSprint = int(request.args.get('idSprint',1))
    
    if "actor" in session:
        res['actor']=session['actor']

    if 'usuario' not in session:
      res['logout'] = '/'
      return json.dumps(res)
    res['usuario'] = session['usuario']

    # Buscamos el actor actual
    oSprint = sprints()
    sprint  = oSprint.searchIdSprint(idSprint,idPila)[0]
    listaHistorias = oSprint.getAssignedSprintHistory(idSprint, idPila) #Obtenes las historias asignadas al sprint

    res['fSprint'] = {'idSprint':idSprint, 'numero':sprint.S_numero, 'descripcion':sprint.S_sprintDescription}

    #Lista de Historias
    res['data5'] = [
        {'idHistoria':historia.UH_idUserHistory,'prioridad':historia.UH_scale, 'enunciado':historia.UH_codeUserHistory}for historia in listaHistorias
    ]

    listaTareas = oSprint.getAssignedSprintTask(idSprint, idPila) # Tareas asignadas al Sprint
    #Lista de tareas
    res['data7'] = [{'idTarea':tarea.HW_idTask, 'descripcion':tarea.HW_description}for tarea in listaTareas]

    session['idSprint'] = idSprint
    res['idSprint'] = idSprint
    res['idPila'] = idPila


    return json.dumps(res)



@sprint.route('/sprint/VSprintHistoria')
def VSprintHistoria():
    #GET parameter
    idSprint = request.args['idSprint']
    res = {}
    if "actor" in session:
        res['actor']=session['actor']

    if 'usuario' not in session:
        res['logout'] = '/'
        return json.dumps(res)
    res['usuario'] = session['usuario']

    idPila = int(session['idPila'])

    oUserHistory = userHistory()
    historiasProducto = oUserHistory.getAllUserHistoryId(idPila)
    res['fSprintHistoria_opcionesHistoria'] = [
        {'key':historia.UH_idUserHistory,'value':historia.UH_codeUserHistory} for historia in historiasProducto
    ]

    res['idSprint']= idSprint
    res['fSprintHistoria'] = {'idPila':idPila, 'idSprint':idSprint}

    return json.dumps(res)



@sprint.route('/sprint/VSprintTarea')
def VSprintTarea():
    #GET parameter
    idSprint = request.args['idSprint']
    res = {}
    if "actor" in session:
        res['actor']=session['actor']

    if 'usuario' not in session:
        res['logout'] = '/'
        return json.dumps(res)

    idPila = int(session['idPila'])
    idSprint = int(request.args['idSprint'])
    oSprint = sprints()
    listaHistorias = oSprint.getAssignedSprintHistory(idSprint, idPila) #Obtenemos las historias asignadas al sprint
    oTask = task()

    #Obtenemos Todas las tareas asociadas a todas nuestras historias
    listaTareas = []
    for historia in listaHistorias:
        tareas = oTask.taskAsociatedToUserHistory(historia.UH_idUserHistory) #Lista de tareas asociada a la historia
        for tarea in tareas:
            listaTareas.append(tarea) #Agregamos todas las tareas de la lista de tareas

    res['fSprintTarea_opcionesTarea'] = [{'key':tarea.HW_idTask,'value':tarea.HW_description}for tarea in listaTareas]
    res['fSprintTarea'] = {'idPila':idPila, 'idSprint':idSprint}

    res['idSprint']= idSprint
    res['usuario'] = session['usuario']
    return json.dumps(res)



@sprint.route('/sprint/VSprints')
def VSprints():
    #GET parameter
    res = {}
    
    # Obtenemos el id del producto.
    idPila = int(request.args.get('idPila',1)) 

    if "actor" in session:
        res['actor']=session['actor']

    if 'usuario' not in session:
      res['logout'] = '/'
      return json.dumps(res)

    res['usuario'] = session['usuario']

    oBacklog   = backlog()
    sprintList = oBacklog.sprintsAsociatedToProduct(idPila)
    res['data1'] = [{'numero':spr.S_numero, 'descripcion':spr.S_sprintDescription } for spr in sprintList]


    session['idPila'] = idPila
    res['idPila']     = idPila 
 
    return json.dumps(res)





#Use case code starts here


#Use case code ends here

