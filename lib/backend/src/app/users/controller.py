# from app.users.models import *
from datetime import datetime

PARAMS = {'1': 'Nodeinfo',
          '2': 'Loadavg',
          '3': 'Memory',
          '4': 'CPU',
          '5': 'Network',
          '6': 'Disk'}

TYPES = {'1': 'JSON',
         '2': 'CSV'}

# def create_report(username, form_data, datafiles, datapath):
#     """
#     To upload a new report.
#     """
#     user = User.objects.get(username=username)
#     gr = Graph(x='rate',
#                y='amount',
#                data=datafiles,
#                data_type = TYPES[form_data.file_type.data],
#                parameter_name = PARAMS[form_data.parameters.data])
#
#     anl = Plots(graphs = [gr])
#     rep = Report(goal=form_data.goal.data,
#                  summary = form_data.summary.data,
#                  results = form_data.results.data,
#                  analysis = anl,
#                  datapath = datapath,
#                  modified = datetime.now(),
#                  created = datetime.now())
#     user.reports[form_data.report_id.data] = rep
#     user.save()
#
# def delete_report(username, report_id):
#     """
#     To delete a report.
#     """
#     try:
#         user = User.objects.get(username=username)
#         user.reports.pop(report_id)
#         user.save()
#         return True
#     except:
#         return False
