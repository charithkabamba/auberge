class WishlistCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Add wishlist_count as a property to the user object
            request.user.wishlist_count = request.user.wishlist.count()
        
        response = self.get_response(request)
        return response 