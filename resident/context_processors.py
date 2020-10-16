from users.models import Flats
from .models import Notice, Complaint

def getSelectedFlat(request):
	if request.user.is_authenticated and not request.user.is_staff and request.session.get("flat"):
		flat = Flats.objects.get(pk=request.session["flat"])
		return {'flat': flat}
	return {}


def getNotice(request):
	notices = Notice.objects.filter(status=1).order_by("-dt")
	return {"notices": notices, "notices_count": len(notices)}


def getComplaints(request):
	if request.user.is_staff:
		new_comp = Complaint.objects.filter(status=1)
		in_comp = Complaint.objects.filter(status=2)
		return {"new_comp": new_comp, "in_comp": in_comp}
	return {}