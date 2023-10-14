import ana_core as ac

excel_file = "拉格朗日开箱统计.xlsx"

container = ac.read_excel(excel_file)

container.print_all()

