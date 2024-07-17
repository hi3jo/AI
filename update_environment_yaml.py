import yaml
import subprocess

# 환경 파일 로드
with open('environment.yaml', 'r') as file:
    env_data = yaml.safe_load(file)

# 'prefix' 키 제거
if 'prefix' in env_data:
    del env_data['prefix']

# 'dependencies' 키가 없는 경우 또는 빈 경우 conda list 명령어로 설치된 패키지 가져오기
if not env_data.get('dependencies') or len(env_data['dependencies']) == 0:
    result = subprocess.run(['conda', 'list', '--export'], stdout=subprocess.PIPE, text=True)
    dependencies = result.stdout.split('\n')
    dependencies = [dep for dep in dependencies if dep and not dep.startswith('#')]
    env_data['dependencies'] = dependencies

# 수정된 환경 파일 저장
with open('environment.yaml', 'w') as file:
    yaml.safe_dump(env_data, file, default_flow_style=False)

print("Updated environment.yaml without prefix and ensured dependencies are listed.")
