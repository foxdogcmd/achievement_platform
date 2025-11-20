from flask import Blueprint, request, jsonify, redirect, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..models.user import User
from ..models.class_model import Class
from .. import db

auth_bp = Blueprint('auth', __name__)

def _get_cas_serializer():
    """创建 CAS 注册用的短期签名序列化器"""
    secret = current_app.config.get('SECRET_KEY') or 'dev-secret'
    return URLSafeTimedSerializer(secret_key=secret, salt='cas-register')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'message': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        password = data.get('password')
        class_id = data.get('class_id')

        # 必须通过 CAS 获取的注册令牌，否则拒绝注册
        cas_token = data.get('cas_token')
        if not cas_token:
            return jsonify({'message': '必须通过 CAS 获取学号/工号后才能注册'}), 400

        # 解析 CAS 注册令牌（短期有效，例如 10 分钟）
        try:
            serializer = _get_cas_serializer()
            payload = serializer.loads(cas_token, max_age=600)
        except SignatureExpired:
            return jsonify({'message': 'CAS 注册令牌已过期，请重新获取'}), 400
        except BadSignature:
            return jsonify({'message': 'CAS 注册令牌无效'}), 400

        username = str(payload.get('uid') or '').strip()
        name = str(payload.get('cn') or '').strip()
        # 根据学号/工号自动判定角色：12位纯数字为学生，否则为队长（枚举值为 team_leader）
        role = 'student' if (username.isdigit() and len(username) == 12) else 'team_leader'
        
        # 验证必填字段
        if not all([username, password, name]):
            return jsonify({'message': '用户名、密码和姓名不能为空'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 班级校验：学生必须选择有效班级；队长可选填班级但若选择则需有效
        if role == 'student':
            if not class_id:
                return jsonify({'message': '学生注册必须选择班级'}), 400
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({'message': '指定的班级不存在'}), 400
        else:
            if class_id:
                class_obj = Class.query.get(class_id)
                if not class_obj:
                    return jsonify({'message': '指定的班级不存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            name=name,
            role=role,
            class_id=class_id if class_id else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': '用户不存在或已被禁用'}), 401
        
        new_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': new_token}), 200
        
    except Exception as e:
        return jsonify({'message': f'刷新令牌失败: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新当前用户的个人信息（仅允许修改姓名）"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'message': '用户不存在'}), 404

        data = request.get_json() or {}
        name = data.get('name')

        if name is None or not str(name).strip():
            return jsonify({'message': '姓名不能为空'}), 400

        # 仅允许修改姓名，避免普通用户随意更改角色/班级
        user.name = str(name).strip()

        db.session.commit()

        return jsonify({
            'message': '个人信息更新成功',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新个人信息失败: {str(e)}'}), 500

@auth_bp.route('/change_password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改当前用户密码，需要提供旧密码进行验证"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'message': '用户不存在'}), 404

        data = request.get_json() or {}
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'message': '旧密码和新密码均为必填'}), 400

        if not user.check_password(old_password):
            return jsonify({'message': '旧密码不正确'}), 400

        if len(new_password) < 6:
            return jsonify({'message': '新密码长度至少为6位'}), 400

        user.set_password(new_password)
        db.session.commit()

        return jsonify({'message': '密码修改成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'密码修改失败: {str(e)}'}), 500

# ===== CAS 调试接口：用于获取返回字段 =====
@auth_bp.route('/cas/start', methods=['GET'])
def cas_start():
    """跳转至 CAS 认证页面（可选注册模式与前端回跳）"""
    try:
        cas_base = current_app.config.get('CAS_BASE_URL')
        base_service = current_app.config.get('CAS_CALLBACK_URL')
        if not cas_base or not base_service:
            return jsonify({'message': 'CAS 配置缺失，请检查 CAS_BASE_URL 与 CAS_CALLBACK_URL'}), 500

        mode = request.args.get('mode')  # 例如 'register'
        return_to = request.args.get('return_to')  # 前端回跳地址，如 http://localhost:8080/register

        from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

        # 将 mode/return_to 透传给 callback，便于回跳
        service_parts = list(urlparse(base_service))
        existing_qs = parse_qs(service_parts[4])
        if mode:
            existing_qs['mode'] = [mode]
        if return_to:
            existing_qs['return_to'] = [return_to]
        service_parts[4] = urlencode(existing_qs, doseq=True)
        service_with_params = urlunparse(service_parts)

        # 构造认证地址：/idp/authCenter/authenticate?service=<回调>
        query = urlencode({'service': service_with_params})
        auth_url = f"{cas_base}/idp/authCenter/authenticate?{query}"
        return redirect(auth_url)
    except Exception as e:
        return jsonify({'message': f'CAS 跳转失败: {str(e)}'}), 500


@auth_bp.route('/cas/callback', methods=['GET'])
def cas_callback():
    """CAS 回调：校验 ST；支持调试回显或注册模式回跳前端"""
    try:
        ticket = request.args.get('ticket')
        mode = request.args.get('mode')
        return_to = request.args.get('return_to')
        if not ticket:
            return jsonify({'message': '缺少 ticket 参数'}), 400

        cas_base = current_app.config.get('CAS_BASE_URL')
        # 注意：service 必须与 CAS 发起时的 service 完全一致（含查询参数）
        from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
        base_service = current_app.config.get('CAS_CALLBACK_URL')
        service_parts = list(urlparse(base_service))
        existing_qs = parse_qs(service_parts[4])
        if mode:
            existing_qs['mode'] = [mode]
        if return_to:
            existing_qs['return_to'] = [return_to]
        service_parts[4] = urlencode(existing_qs, doseq=True)
        service = urlunparse(service_parts)

        if not cas_base or not service:
            return jsonify({'message': 'CAS 配置缺失，请检查 CAS_BASE_URL 与 CAS_CALLBACK_URL'}), 500

        from urllib.request import urlopen
        import json

        # 使用 JSON 格式以便直接解析字段
        query = urlencode({'ticket': ticket, 'service': service, 'format': 'json'})
        validate_url = f"{cas_base}/idp/cas/p3/serviceValidate?{query}"

        try:
            with urlopen(validate_url, timeout=10) as resp:
                payload = resp.read().decode('utf-8')
        except Exception as net_err:
            return jsonify({'message': 'CAS 校验请求失败', 'error': str(net_err), 'validate_url': validate_url}), 502

        # 解析 JSON
        try:
            data = json.loads(payload)
        except Exception:
            data = {'raw': payload}

        # 如果是注册模式，提取 uid 与 cn，签发一次性注册令牌并回跳前端
        if mode == 'register' and return_to:
            # 兼容不同 JSON 结构（serviceResponse 可能嵌套）
            sr = data.get('serviceResponse') or {}
            if 'serviceResponse' in sr:
                sr = sr.get('serviceResponse') or {}
            auth = sr.get('authenticationSuccess') or {}
            attrs = auth.get('attributes') or {}

            uid = attrs.get('uid') or auth.get('user')  # 优先 uid，回退 user
            cn = attrs.get('cn') or attrs.get('user_name') or ''
            if not uid:
                return jsonify({'message': 'CAS 返回缺少 uid/user 字段，无法完成注册'}), 400

            # 生成一次性注册令牌（包含 uid/cn），短期有效
            serializer = _get_cas_serializer()
            reg_token = serializer.dumps({'uid': uid, 'cn': cn})

            # 拼接回跳地址：携带 from=cas、token
            rt_parts = list(urlparse(return_to))
            rt_qs = parse_qs(rt_parts[4])
            rt_qs['from'] = ['cas']
            rt_qs['token'] = [reg_token]
            rt_parts[4] = urlencode(rt_qs, doseq=True)
            final_url = urlunparse(rt_parts)
            return redirect(final_url)

        # 默认：调试回显 JSON
        return jsonify({
            'message': 'CAS 校验完成（用于调试）',
            'validate_url': validate_url,
            'ticket': ticket,
            'serviceResponse': data
        }), 200
    except Exception as e:
        return jsonify({'message': f'CAS 回调处理失败: {str(e)}'}), 500

@auth_bp.route('/cas/token_info', methods=['GET'])
def cas_token_info():
    """解析 CAS 注册令牌，返回 uid/cn 供前端展示"""
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({'message': '缺少 token 参数'}), 400
        serializer = _get_cas_serializer()
        try:
            payload = serializer.loads(token, max_age=600)
        except SignatureExpired:
            return jsonify({'message': 'CAS 注册令牌已过期'}), 400
        except BadSignature:
            return jsonify({'message': 'CAS 注册令牌无效'}), 400
        uid = str(payload.get('uid') or '').strip()
        cn = str(payload.get('cn') or '').strip()
        if not uid:
            return jsonify({'message': '令牌中缺少 uid'}), 400
        return jsonify({'uid': uid, 'cn': cn}), 200
    except Exception as e:
        return jsonify({'message': f'解析令牌失败: {str(e)}'}), 500