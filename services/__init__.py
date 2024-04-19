"""Services."""

from services.user_service import UserService
from services.paper_service import PaperService
from services.paper_group_service import PaperGroupService
from services.paper_group_info_service import PaperGroupInfoService

user_service = UserService()
paper_service = PaperService()
paper_group_service = PaperGroupService()
paper_group_info_service = PaperGroupInfoService()
