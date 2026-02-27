from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import MeSerializer
from providers.models import Service


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == "GET":
        return Response(MeSerializer(request.user, context={'request': request}).data)
    # PATCH: update provider profile (image, description, address, city, country, lat/lng)
    if not hasattr(request.user, 'provider_profile'):
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_403_FORBIDDEN)
    prov = request.user.provider_profile
    for field in ('description', 'address', 'city', 'country'):
        if field in request.data:
            val = (request.data.get(field) or '')[:255] if field != 'description' else (request.data.get(field) or '')[:200]
            setattr(prov, field, val)
    if 'latitude' in request.data:
        try:
            prov.latitude = float(request.data.get('latitude')) if request.data.get('latitude') not in (None, '') else None
        except (TypeError, ValueError):
            pass
    if 'longitude' in request.data:
        try:
            prov.longitude = float(request.data.get('longitude')) if request.data.get('longitude') not in (None, '') else None
        except (TypeError, ValueError):
            pass
    if 'image' in request.FILES:
        prov.image = request.FILES['image']
    prov.save()
    return Response(MeSerializer(request.user, context={'request': request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_service(request):
    if not hasattr(request.user, 'provider_profile'):
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_403_FORBIDDEN)
    provider = request.user.provider_profile
    name = (request.data.get('name') or '').strip()
    price_cents = request.data.get('price_cents')
    if price_cents is None:
        price = request.data.get('price')
        price_cents = int(round((float(price) if price else 0) * 100))
    description = (request.data.get('description') or '').strip()
    duration_minutes = request.data.get('duration_minutes', 60)
    if not name:
        return Response({'error': 'Service name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if price_cents < 0:
        return Response({'error': 'Price must be non-negative'}, status=status.HTTP_400_BAD_REQUEST)
    svc = Service.objects.create(
        provider=provider,
        name=name,
        description=description,
        price_cents=price_cents,
        duration_minutes=duration_minutes or 60,
        is_active=True,
    )
    return Response({
        'id': svc.id,
        'name': svc.name,
        'description': svc.description,
        'price_cents': svc.price_cents,
        'duration_minutes': svc.duration_minutes,
        'is_active': svc.is_active,
    }, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def service_detail(request, pk):
    if not hasattr(request.user, 'provider_profile'):
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_403_FORBIDDEN)
    provider = request.user.provider_profile
    try:
        svc = Service.objects.get(pk=pk, provider=provider)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        svc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # PATCH / PUT
    name = request.data.get('name')
    if name is not None:
        name = (name or '').strip()
        if not name:
            return Response({'error': 'Service name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        svc.name = name
    description = request.data.get('description')
    if description is not None:
        svc.description = (description or '').strip()
    price_cents = request.data.get('price_cents')
    if price_cents is None:
        price = request.data.get('price')
        if price is not None:
            price_cents = int(round((float(price) if price else 0) * 100))
    if price_cents is not None:
        if price_cents < 0:
            return Response({'error': 'Price must be non-negative'}, status=status.HTTP_400_BAD_REQUEST)
        svc.price_cents = price_cents
    duration_minutes = request.data.get('duration_minutes')
    if duration_minutes is not None:
        svc.duration_minutes = duration_minutes or 60
    svc.save()
    return Response({
        'id': svc.id,
        'name': svc.name,
        'description': svc.description,
        'price_cents': svc.price_cents,
        'duration_minutes': svc.duration_minutes,
        'is_active': svc.is_active,
    })
