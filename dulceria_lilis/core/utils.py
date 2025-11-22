import openpyxl
from django.http import HttpResponse

def export_to_excel(headers, data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Datos"

    # Encabezados
    ws.append(headers)

    # Datos
    for row in data:
        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

    wb.save(response)
    return response
