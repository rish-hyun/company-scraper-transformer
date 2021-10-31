import os
from fpdf import FPDF


class PDF(FPDF):
    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class ExportToPDF:

    def export_to_pdf(self, item):

        [item.pop(key, None) for key in ['_id', 'ID', 'content', 'transform']]
        company_name = item['Company Name']

        # Instantiation of inherited class
        pdf = PDF()
        margin = 6 #pdf.l_margin  # Page margin
        pdf.set_margins(margin, margin)
        pdf.alias_nb_pages()

        pdf.add_page()
        pdf.set_font('Arial', 'B', 8)

        sno_width = 10  # Serial Number width
        col_width = (pdf.w-(2*margin)-sno_width)
        key_width = col_width * 0.25
        val_width = col_width * 0.75

        row_height = pdf.font_size + 2

        pdf.set_font('Arial', 'BU', 18)
        pdf.cell(0, 15, txt=f'{company_name} Report', border=1, ln=1, align='C')
        pdf.ln(15)

        pdf.set_font('Arial', 'BIU', 8)
        pdf.cell(sno_width, row_height, txt='S.No', border=1, ln=0, align='C')
        pdf.cell(key_width, row_height, txt='Parameter', border=1, ln=0, align='C')
        pdf.cell(val_width, row_height, txt='Value', border=1, ln=1, align='C')

        count = 0
        pdf.set_font('Arial', '', 8)
        for key, val in item.items():

            count += 1
            if type(val) == list and len(val) > 1:
                scale = len(val)-1 if len(val) > 1 else 0
                change_count = 0
                for line in val:
                    change = pdf.get_string_width(line) // val_width
                    scale += change
                    if change > 0:
                        change_count += 1
                if change_count != 0:
                    scale += (change_count-1)

            else:
                val = str(val)
                scale = pdf.get_string_width(val) // val_width

            row_hgt = row_height + (row_height * scale)

            if scale:
                pdf.cell(sno_width, row_hgt, txt=str(count), border=1, ln=0, align='C')
                pdf.cell(key_width, row_hgt, txt=key, border=1, ln=0)

                for i in range(len(val)):
                    scale = pdf.get_string_width(val[i]) // val_width

                    step = int(len(val[i])//(scale + 1)) - 1
                    order = list(range(0, len(val[i]), step))

                    for j in order[:-1]:
                        start = j
                        end = j + step

                        if start == order[0]:
                            border, ln = 'LR', 2
                            if i == 0:
                                border = 'LTR'

                        if end == order[-1]:
                            end = len(val[i])
                            border, ln = 'LR', 2
                            if i == len(val)-1:
                                border, ln = 'LBR', 1

                        else:
                            border, ln = 'LR', 2

                        pdf.cell(val_width, row_height, txt=val[i][start:end], border=border, ln=ln)

                    if scale > 0 and i < len(val)-1:
                        pdf.cell(val_width, row_height, txt='', border='LR', ln=2)

            else:
                pdf.cell(sno_width, row_height, txt=str(count), border=1, ln=0, align='C')
                pdf.cell(key_width, row_height, txt=key, border=1, ln=0)
                pdf.cell(val_width, row_height, txt=val, border=1, ln=1)

        pdf.output(f'{company_name}.pdf', 'F')
        os.startfile(f'{company_name}.pdf')

