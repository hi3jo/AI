# 1 공통 설정 모듈
# 이 모듈은 경고 메시지 무시 설정과 로그 설정을 포함

import warnings
import logging

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning)

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)