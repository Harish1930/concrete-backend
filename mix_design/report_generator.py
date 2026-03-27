from reportlab.pdfgen import canvas


def generate_report(result):

    pdf=canvas.Canvas("mix_design_report.pdf")

    y=800

    pdf.setFont("Helvetica",12)

    pdf.drawString(200,820,"Concrete Mix Design Report")

    for key,value in result.items():

        pdf.drawString(100,y,f"{key}: {value}")

        y-=25

    pdf.save()