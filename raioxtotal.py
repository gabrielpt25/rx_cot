import sys, os, time, datetime, plistlib, subprocess, gzip
from PyQt5 import QtWidgets, QtGui,uic
from PyQt5.QtWidgets import QMessageBox
from dateutil import relativedelta

# lista dos diretórios a serem percorridos do servidor
server_directories_list = ["\\\\192.0.0.253\\imagens_u02$\\", "\\\\192.0.0.253\\imagens_u03$\\",
                           "\\\\192.0.0.253\\imagens_u04$\\"
    , "\\\\192.0.0.253\\imagens_u05$\\", "\\\\192.0.0.253\\imagens_u06$\\", "\\\\192.0.0.253\\imagens_u07$\\",
                           "\\\\192.0.0.253\\imagens_u08$\\", "\\\\192.0.0.253\\imagens_u09$\\"]

# Lista de armazenamento dos caminhos absolutos dos arquivos
local_file_list = []

# variavéis "globais"
user_local_directory = "C:\\smart\\dicom\\conquest\\data\\"
server_files = []
modification_file_time = []


def search_button():
    if len(modification_file_time) > 1:
        modification_file_time.clear()
    reg_pac = str(raiox_total.lineEdit.text())
    raiox_total.listWidget_2.clear()
    index_dir_list = 0
    index_server_files = 0
    today = datetime.date.today()
    passed_date_months = []

    if reg_pac:

        # Percorre a lista de diretórios do servidor buscando as imagens do paciente.
        while (index_dir_list < len(server_directories_list)):
            absolute_server_directory = server_directories_list[index_dir_list] + reg_pac

            for root, dirs, files in os.walk(absolute_server_directory):
                for filename in files:
                    absolute_file_path = str(root + "\\" + filename)
                    file_mtime = os.path.getmtime(absolute_file_path)
                    # Converte de os.path.getmtime para padrão definido usando a função datetime.datetime.fromtimestamp
                    modification_file = datetime.datetime.fromtimestamp(file_mtime).strftime('%d-%m-%Y')
                    server_files.append(absolute_file_path)
                    modification_file_time.append(modification_file)
            index_dir_list += 1

        try:
            while (index_server_files < len(server_files)):
                user_local_directory = "C:\\smart\\dicom\\conquest\\data\\" + reg_pac + "\\"
                os.mkdir(user_local_directory)
                file = server_files[index_server_files]
                file_mtime = os.path.getmtime(file)
                # Converte de os.path.getmtime para padrão definido usando a função datetime.datetime.fromtimestamp
                modification_file = datetime.datetime.fromtimestamp(file_mtime).strftime('%d-%m-%Y')
                date_dir_name = user_local_directory + modification_file
                index_server_files += 1
        except FileExistsError:
            index_server_files += 1
        print("antes de limpar a lista")


        # organiza a lista de data por ordem crescente
        modification_file_time.sort(key=lambda date: datetime.datetime.strptime(date, '%d-%m-%Y'))

        # Retorna quantidade de arquivos por data
        date_dict = {i: modification_file_time.count(i) for i in modification_file_time}

        # Retorna data como a chave, e valor como quantidade de arquivos.
        i = 0

        # duplicateFrequencies = {}
        # for i in set(modification_file_time):
        #     duplicateFrequencies[i] = modification_file_time.count(i)
        # print(duplicateFrequencies)


        for key in date_dict:
            user_local_directory_1 = "C:\\smart\\dicom\\conquest\\data\\" + reg_pac + "\\" + key
            raiox_total.listWidget_2.addItem(key)
            # raiox_total.listView.addItem(date_dict[key])
            try:
                os.mkdir(user_local_directory_1)
            except FileExistsError:
                continue
    else:
        QMessageBox.about(raiox_total, "Alerta", "Favor informar registro do paciente!")


# função para abrir as imagens quando der o duplo clique em cima da data
def image_view():
    # pega o valor do item selecionado.
    # image_date = raiox_total.listWidget_2.currentItem()
    reg_pac = str(raiox_total.lineEdit.text())
    modification_file = ""
    dest_local_path = ""
    index_dir_list = 0
    index_server_files = 0
    server_files = []

    # Percorre a lista de diretórios do servidor buscando as imagens do paciente.
    while (index_dir_list < len(server_directories_list)):
        print("entrei no while")
        absolute_server_directory = server_directories_list[index_dir_list] + reg_pac
        patient_reg_id = reg_pac

        for root, dirs, files in os.walk(absolute_server_directory):
            image_date = raiox_total.listWidget_2.currentItem()
            print("entrei no primeiro for")
            for filename in files:
                print("entrei no segundo for")
                absolute_server_file_path = str(root + "\\" + filename)
                file_mtime = os.path.getmtime(absolute_server_file_path)
                # Converte de os.path.getmtime para padrão definido usando a função datetime.datetime.fromtimestamp
                modification_file = datetime.datetime.fromtimestamp(file_mtime).strftime('%d-%m-%Y')
                # testa se a data do arquivo com os arquivos no servidor e copia as mesmas para a pasta local
                print(image_date.text())
                print("caminho do arquivo: " + absolute_server_file_path)
                if (modification_file == image_date.text()):
                    print("entrei no if que testa os diretorios para copiar")
                    dest_local_path = user_local_directory + reg_pac + "\\" + modification_file
                    print(dest_local_path)
                    # copia os arquivos para a máquina do usuário
                    os.system("1>NUL xcopy %s %s /Q /K /D /H /Y" % (absolute_server_file_path, dest_local_path))

                server_files.append(absolute_server_file_path)
                # modification_file_time.append(modification_file)
        index_dir_list += 1
    if (os.path.isdir(dest_local_path) and len(os.listdir(dest_local_path)) != 0):
        for filename in os.listdir(dest_local_path):
            if filename.lower().endswith(('.gz')):
                total_file_path = dest_local_path + "\\" + filename
                input = gzip.GzipFile(total_file_path, 'rb')
                s = input.read()
                input.close()

                output = open(total_file_path.strip(".gz"), 'wb')
                output.write(s)
                output.close()
                print("done")
                os.remove(total_file_path)

        subprocess.Popen(["C:\MicroDicom\mDicom.exe", dest_local_path])
    else:
        print("Diretório vazio ou não criado.")


app = QtWidgets.QApplication([])
raiox_total = uic.loadUi("raiox1.ui")
#quando for pressionado enter realizar a pesquisa (no caso, chamado a funcção search_button)
raiox_total.lineEdit.returnPressed.connect(search_button)
raiox_total.pushButton.clicked.connect(search_button)
raiox_total.listWidget_2.itemDoubleClicked.connect(image_view)
raiox_total.show()
app.exec()