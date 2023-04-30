from flask import *
import re
import os
import zipfile
import shutil

app = Flask(__name__, static_url_path='/static')

configs = {
     "upload_loc" : "./uploads",
     "download_loc" : "./static/downloads",
     "temp" : "./temporary"
}

def extract_zip(src,dest):
    with zipfile.ZipFile(src, 'r') as zip_ref:
        zip_ref.extractall(dest)

def clean_dir(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def create_dirs():
    import os

def create_dirs():
    try:
        os.mkdir("statis/downloads")
    except:
        print("LOG : static/downloads directory already there")
    try:
        os.mkdir("uploads")
    except:
        print("LOG : uploads directory already there")
    try:
        os.mkdir("temporary")
    except:
        print("LOG : temporary directory already there")

create_dirs()

@app.route("/home", methods = ["GET","POST"])
def generateParams():
    create_dirs()
    clean_dir(configs['download_loc'])
    clean_dir(configs['temp'])
    clean_dir(configs['upload_loc'])

    log_file_folder_path = ""
    parameter_name = ""
    path = ""

    apiOutput = {}
    input_json = {}
    # input_json = request.get_json(force=True) 
    if request.method == "POST":
        file = request.files['LogFile']
        parameterName = request.form['ParameterName']
        file.save(os.path.join(configs['upload_loc'], file.filename))
        zip_loc = os.path.join(configs['upload_loc'], file.filename)
        output_loc = configs['temp']
        try:
            extract_zip(zip_loc, output_loc)
            print("LOG : Zip extracted successfully")
        except:
            print("LOG : Zip extraction failed")


        log_file_folder_path = configs['temp']
        parameter_name = str(parameterName)
        path = configs['download_loc']
        

        count = 0
        if len(log_file_folder_path) != 0 and len(parameter_name) != 0 and len(path) != 0:
            try:
                logFileList = list(os.listdir(log_file_folder_path))
                def readLogfile(file_path):
                        file = open(file_path, "r")
                        raw_data = file.read()
                        file.close()
                        return raw_data

                parameters = []
                k = 1
                for file in logFileList:
                    file_path = os.path.join(log_file_folder_path, file)
                    content = readLogfile(file_path)
                    paramList = re.findall(f"\"{parameter_name}\" = \"(.+?)\"", content)
                    # print(f"{k}. {paramList}")
                    # k = k+1
                    if len(paramList) != 0:
                        for param in paramList:
                            parameters.append(param)
                    else:
                            count += 1
                # print(count)
                if count != len(logFileList):
                    paramFileContent = ""
                    paramFileContent += parameter_name + "\n"
                    for parameter in parameters:
                        paramFileContent += parameter + "\n"

                    parameter_file_name = "output.csv"
                    outputFile = open(os.path.join(path, parameter_file_name), "w")
                    outputFile.write(paramFileContent)
                    outputFile.close()
                    
                    apiOutput["message"] = "Parameter generated successfully"
                    apiOutput["output_file_path"] = str(os.path.join(path, parameter_file_name))
                else:
                    apiOutput["error_message"] = "The parameter does not exists in the log files"
                # clean_dir(configs['temp'])
                # clean_dir(configs['upload_loc'])
                return send_file("./static/downloads/output.csv", as_attachment=True)                
            except:
                apiOutput["error_message"] = "Could not generate due to some internal server error"
        else:
            apiOutput["error_message"] = "Either payload is empty or provided wrong information"

    print(apiOutput)

    return render_template("index.html")

app.run(debug=True)