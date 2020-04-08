from flask import Flask, render_template, request, jsonify, send_from_directory, json, make_response
import build
import os
import json
from pathlib import Path
import subprocess

app = Flask(__name__, template_folder='./',
            static_folder="", static_url_path="")


@app.route('/')
@app.route('/index')
def generate_website():
    mods = set()
    enmods = set()
    optionals = set()
    figures = set()
    mods.update(["mods/" + file for file in os.listdir('mods')])
    enmods.update(["en-mods/" + file for file in os.listdir('en-mods')])
    optionals.update(["optional/" + str(file.relative_to('optional/').as_posix())
                      for file in Path('optional').iterdir() if not file.is_dir()])
    figures.update(["optional/" + str(file.relative_to('optional/').as_posix())
                    for file in Path('optional').iterdir() if file.is_dir()])
    header_existance = os.path.exists("custom/header.html")
    footer_existance = os.path.exists("custom/footer.html")
    return render_template("./index.html", mods=mods, enmods=enmods, optionals=optionals, figures=figures, header_existance=header_existance, footer_existance=footer_existance)


@app.route('/ajax', methods=['POST'])
def ajax():
    recv_data = json.loads(request.get_data('data'))
    p = subprocess.Popen(["git", "pull", "origin", "master"],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    p.wait()
    logs = str(p.communicate()[0], 'utf-8', 'ignore')
    result = build.build(recv_data)
    logs += result[1]
    message = {"code": 200, "argument": recv_data,
               "logs": logs, "filename": result[0]}
    return json.dumps(message)


@app.route('/files/<file_name>', methods=['GET'])
def get_file(file_name):
    directory = "./"
    try:
        response = make_response(send_from_directory(
            directory, file_name, as_attachment=True))
        return response
    except Exception as e:
        return jsonify({"code": "500", "message": "{}".format(e)})


if __name__ == '__main__':
    app.run(threaded=True)
