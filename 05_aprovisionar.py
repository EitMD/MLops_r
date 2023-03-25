
import os
import sys, getopt
import time
import boto3

if 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ and 'AWS_DEFAULT_REGION' in os.environ  and 'ACCOUNT_NUMBER' in os.environ:
 if len(sys.argv) > 1 :
    argumentList = sys.argv[1:]
    options = "rts"

    arguments, values = getopt.getopt(argumentList, options)

    for currentArgument, currentValue in arguments :
      create_ecr =   True if currentArgument in "-r" else False
      create_task_definition=  True if currentArgument in "-t" else False
      create_service=  True if currentArgument in "-s" else False
 else :
  #no hay nada por hacer
   print("05_aprovisionar: indicer opciones -r -t -s ")
else:
   print("AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY  AWS_DEFAULT_REGION ACCOUNT_NUMBER debe ser configurada")

   exit(1)


if create_ecr : 
   if 'ECR_REPO_NAME' in os.environ : 
      #crear repositorio de imagen de contenedores - Elastic Container Registry
      ecr_cliente = client = boto3.client('ecr')
      print("Creando Registro de Imagen del contenedor con nombre ",os.environ['ECR_REPO_NAME'])
      client.create_repository(repositoryName=os.environ['ECR_REPO_NAME'])
   else :
      print("ECR_REPO_NAME debe ser configurada")
      exit(2)
if create_task_definition or create_service :
    ecs_cliente = boto3.client('ecs')

    if create_task_definition : 
       #crear defincion de Tarea
       
       if 'ECR_REPO_NAME' in os.environ :
         task_name = 'task{}'.format(os.environ['ECR_REPO_NAME'])
         print("Creando Definicion de Tarea de ECS ",task_name)
         roleArn = 'arn:aws:iam::{}:role/ecsTaskExecutionRole'.format(os.environ['ACCOUNT_NUMBER'])
         print("executionRoleArn",roleArn)
         datos_tarea=ecs_cliente.register_task_definition( 
            family=task_name,
            cpu ='256',
            memory = '512',
            requiresCompatibilities= ['FARGATE'],
            runtimePlatform = {'cpuArchitecture': 'X86_64', 'operatingSystemFamily': 'LINUX'},
            networkMode = 'awsvpc' ,
            executionRoleArn = roleArn,
            containerDefinitions=[
             { 
                'name': os.environ['ECR_REPO_NAME'],
                'image': '{}.dkr.ecr.{}.amazonaws.com/{}'.format(os.environ['ACCOUNT_NUMBER'],os.environ ['AWS_DEFAULT_REGION'],os.environ['ECR_REPO_NAME']) ,
                'portMappings': [{'containerPort': 5000, 'hostPort': 5000, 'protocol': 'tcp', 'name': '{}-5000-tcp'.format(os.environ['ECR_REPO_NAME']),
                              'appProtocol': 'http'}] ,
             }
           ] 
         )
         print("Datos de tarea", datos_tarea)
       else :
           print("ECR_REPO_NAME debe ser configurada")
           exit(3)
    if create_service :
       if 'ECR_REPO_NAME' in os.environ  and 'SERVICE_NAME' in os.environ and 'ECS_CLUSTER' in  os.environ and  'SG_SERVICE' in  os.environ  and 'SUB01' in  os.environ   and 'SUB02' in  os.environ and  'VERSION_TASKDEF'  in  os.environ   :
        #Crear servicio
        service_name = os.environ['SERVICE_NAME']
        print("Creando Servicio de ECS ",service_name)
        task_name = 'task{}'.format(os.environ['ECR_REPO_NAME'])
        svc_info=ecs_cliente.create_service(cluster= os.environ ['ECS_CLUSTER'],
                           serviceName=service_name,
                           taskDefinition='arn:aws:ecs:{}:{}:task-definition/{}:{}'.format(os.environ ['AWS_DEFAULT_REGION'],os.environ['ACCOUNT_NUMBER'],task_name,os.environ['VERSION_TASKDEF']),
                           launchType ='FARGATE',
                           desiredCount=1,
                           networkConfiguration= {
                               'awsvpcConfiguration': {
                                  'assignPublicIp' : 'ENABLED',
                                  'securityGroups': [ os.environ ['SG_SERVICE']],
                                  'subnets': [ os.environ ['SUB01'] ,  os.environ ['SUB02'] ],
                                }   
                            }
                          )
        print("Datos del servicion",svc_info)
       else :
           print("ECR_REPO_NAME SERVICE_NAME ECS_CLUSTER SG_SERVICE SUB01 SUB02 VERSION_TASKDEF debe ser configurada")
           for variable in str.split("ECR_REPO_NAME SERVICE_NAME ECS_CLUSTER SG_SERVICE SUB01 SUB02 VERSION_TASKDEF") :
             if variable in os.environ :
               print(os.environ[variable]) 
             else :
               print("Variable de ambiente no configurada", variable)
           exit(4)                 

#mostrar definciones de tare y servicios en JSON
#ecs_cliente.describe_task_definition( taskDefinition='tskdummylinear2') 

#ecs_cliente.describe_services(cluster='dummylinear',services=["svcdummylinear"])
