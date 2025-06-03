import io
from openpyxl import Workbook
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def generate_sensor_history_excel(sensor, mouvements, avant, apres):
    wb = Workbook()
    ws = wb.active
    ws.title = "Historique capteur"

    # 🔹 Infos capteur
    ws.append(["ID", sensor.id])
    ws.append(["Type", sensor.type])
    ws.append(["Sous-type", sensor.subtype])
    ws.append([])

    # 🔹 Mouvements
    ws.append(["--- Mouvements ---"])
    ws.append(["Chantier", "Date départ", "Date retour", "Commentaire"])
    for m in mouvements:
        ws.append([m.chantier, m.date_depart, m.date_retour, m.commentaire])
    ws.append([])

    # 🔹 Checklist avant
    ws.append(["--- Checklist AVANT maintenance ---"])
    ws.append(["Item", "Coché", "Technicien", "Date"])
    for r in avant:
        ws.append([r.label, "✔" if r.is_checked else "✘", r.user.name, r.date_checked])
    ws.append([])

    # 🔹 Checklist après
    ws.append(["--- Checklist APRÈS maintenance ---"])
    ws.append(["Item", "Coché", "Technicien", "Date"])
    for r in apres:
        ws.append([r.label, "✔" if r.is_checked else "✘", r.user.name, r.date_checked])

    # 🔽 Export
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=historique_{sensor.id}.xlsx"}
    )


def generate_sensor_history_pdf(sensor, mouvements, avant, apres):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Historique capteur {sensor.id}")

    x, y = 2 * cm, 28 * cm

    def write_line(text, size=10, bold=False):
        nonlocal y
        if y < 2 * cm:
            pdf.showPage()
            y = 28 * cm
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        pdf.drawString(x, y, str(text))
        y -= 0.6 * cm

    # Infos capteur
    write_line(f"Capteur ID : {sensor.id}", bold=True)
    write_line(f"Type : {sensor.type}")
    write_line(f"Sous-type : {sensor.subtype}")
    write_line("")

    # Mouvements
    write_line("--- Mouvements ---", bold=True)
    for m in mouvements:
        write_line(f"- Chantier : {m.chantier}")
        write_line(f"  Départ : {m.date_depart} | Retour : {m.date_retour}")
        if m.commentaire:
            write_line(f"  Commentaire : {m.commentaire}")
        write_line("")

    # Checklist AVANT
    write_line("--- Checklist AVANT maintenance ---", bold=True)
    for r in avant:
        write_line(f"[{'✔' if r.is_checked else '✘'}] {r.label} par {r.user.name} le {r.date_checked}")
    write_line("")

    # Checklist APRÈS
    write_line("--- Checklist APRÈS maintenance ---", bold=True)
    for r in apres:
        write_line(f"[{'✔' if r.is_checked else '✘'}] {r.label} par {r.user.name} le {r.date_checked}")

    pdf.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=historique_{sensor.id}.pdf"}
    )