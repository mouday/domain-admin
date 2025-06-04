from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)


@app.route('/check', methods=['GET'])
def check_domain():
    # 获取URL参数
    url = request.args.get('url')

    if not url:
        # 参数为空
        return jsonify({
            'code': 202,
            'msg': '请传入Url'
        }), 200

    try:
        # 调用官方接口
        check_url = f'https://cgi.urlsec.qq.com/index.php?m=url&a=validUrl&url={requests.utils.quote(url)}'
        headers = {'Content-Type': 'application/json'}

        # 发送请求
        response = requests.get(check_url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析响应
        data = response.json()
        data_msg = data.get('data', '')

        if data_msg == 'ok':
            # 域名被封
            return jsonify({
                'code': 202,
                'msg': '域名被封'
            }), 200
        else:
            # 域名正常
            return jsonify({
                'code': 200,
                'msg': data_msg
            }), 200

    except requests.exceptions.RequestException as e:
        # 请求异常处理
        return jsonify({
            'code': 500,
            'msg': f'检测失败: {str(e)}'
        }), 200
    except json.JSONDecodeError:
        # JSON解析失败
        return jsonify({
            'code': 500,
            'msg': '接口响应解析失败'
        }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)