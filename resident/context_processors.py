from users.models import Flats

def getSelectedFlat(request):
	if request.user.is_authenticated and not request.user.is_staff and request.session.get("flat"):
		flat = Flats.objects.get(pk=request.session["flat"])
		return {'flat': flat}
	return {}