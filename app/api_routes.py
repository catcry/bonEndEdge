from flask import request, jsonify
from app import app
from app.sql import get_record, insert_record, delete_record
from pydantic import BaseModel
from pydantic import ValidationError
from app.nginx_gen import nginx_conf_gen, nginx_conf_del


### Schemas
class Request(BaseModel):
    end_name: str
    end_url: str
    port: str

class DelRequest(BaseModel):
    end_name: str


@app.route('/api/get_record', methods=['GET'])
def get_end():
    end_name = request.args.get('end_name')
    end_url = request.args.get('end_url')
    port = request.args.get('port')
    result = get_record(end_name, end_url, port)
    return jsonify({"result": result})



@app.route('/api/insert_record', methods=['POST'])
def insert_end():
    try: 
        data = request.get_json()
        req = Request(**data)
        check_record_existence = get_record(req.end_name, req.end_url, req.port)

        if not check_record_existence:
            result_db = insert_record(req.end_name, req.end_url,req.port)
            result_file_push = nginx_conf_gen(req.end_name, req.end_url, req.port)

            if result_db and result_file_push:
                return jsonify({"message": "Record inserted successfully"}), 200
            else:
                return jsonify({"message": "Error Occured in inserting "})
        else:
            return jsonify({"message": "Record already exist", "record" : check_record_existence}), 200
    except ValidationError as e:
        # Handle validation errors
        return jsonify({"error": str(e)}), 400
    
@app.route('/api/delete_end', methods=['DELETE'])
def delete_end():
    try:
        data = request.get_json()
        req = DelRequest(**data)
        result_del_file = nginx_conf_del(req.end_name)
        result_del_db = delete_record(req.end_name)
        #print (result)
        return jsonify({"message": "Record Deleted Successfully"}), 200
    except:
        print ("cannot")

        