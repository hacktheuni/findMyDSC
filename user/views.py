from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import re
from django.contrib.auth.hashers import check_password, make_password

def getUser(request):
    userID = request.session.get('userID')
    subAdminID = request.session.get('subAdminID')
    superAdminID = request.session.get('superAdminID')

    user = None
    base = None
    subAdmin = None
    superAdmin = None

    # Check if it's a user or subAdmin session
    if userID:
        user = UpdatedUser.objects.get(userID=userID)
        base = 'base/userBase.html'
    elif subAdminID:
        subAdmin = SignUP.objects.get(subAdminID=subAdminID)
        user = UpdatedUser.objects.get(userPhone=subAdmin.subAdminPhone)
        base = 'base/subAdminBase.html'
    elif superAdminID:
        superAdmin = SuperAdmin.objects.get(superAdminID=superAdminID)
        base = 'base/superAdminBase.html'
    else:
        return redirect('adminSignIn')

    return {'user': user, 'base': base, 'subAdmin': subAdmin, 'superAdmin': superAdmin}


# All List Function are here
def listDSC(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    whatsapp_url = request.session.pop('whatsapp_url', None)

    updatedDSCs = UpdatedDSC.objects.filter(subAdminID=user.subAdminID).all().order_by('-modifiedDate')
    context = {
        'base': base,
        'updatedDSCs': updatedDSCs,
        'user': user,
        'whatsurl': whatsapp_url 
    }
    return render(request, 'dsc/listDSC.html', context)

def listCompany(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    companies = UpdatedCompany.objects.filter(subAdminID=user.subAdminID).all().order_by('-companyModifiedDate')
    context = {
        'base': base,
        'companies': companies,
        'user': user
    }
    return render(request, 'company/listCompany.html', context)

def listGroup(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    groups = UpdatedGroup.objects.filter(subAdminID=user.subAdminID).all().order_by('-groupModifiedDate')
    context = {
        'base': base,
        'groups':groups,
        'user': user
    }
    return render(request, 'group/listGroup.html', context)

def listClient(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    clients = UpdatedClient.objects.filter(subAdminID=user.subAdminID).all().order_by('-clientModifiedDate')
    context = {
        'base': base,
        'clients': clients,
        'user': user
    }
    return render(request, 'client/listClient.html', context)


# All Add Function are here
def addDSC(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    companies = UpdatedCompany.objects.filter(subAdminID=user.subAdminID).all()
    context = {
        'base': base,
        'companies': companies,
        'user': user
    }

    if request.method == 'POST':
        clientName = request.POST.get('clientName')
        companyName = request.POST.get('companyName')
        status = request.POST.get('status')
        location = request.POST.get('location')
        renewalDate = request.POST.get('renewalDate', '')
        receivedBy = request.POST.get('receivedBy', '')
        receivedFrom = request.POST.get('receivedFrom', '')
        clientPhone = request.POST.get('clientPhone')
        deliveredTo = request.POST.get('deliveredTo', '')

        if not all([clientName, companyName, status, location]):
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)
        else:
            subAdminID = user.subAdminID
            company = UpdatedCompany.objects.filter(companyName=companyName, subAdminID=subAdminID).first()

            if company:
                dsc = UpdatedDSC(
                    clientName=clientName,  companyID=company,  status=status,  receivedBy=receivedBy, receivedFrom=receivedFrom,  deliveredTo=deliveredTo,  location=location,  renewalDate=renewalDate, clientPhone=clientPhone,  userID=user, subAdminID=subAdminID
                )
                dsc.save()

                dscHistory = HistoryDSC(
                    dscID=dsc,  clientName=clientName,  companyID=company,  status=status,  receivedBy=receivedBy, receivedFrom=receivedFrom,  deliveredTo=deliveredTo,  location=location,  renewalDate=renewalDate, clientPhone=clientPhone,  userID=user, subAdminID=subAdminID, modifiedDate=dsc.modifiedDate
                )
                dscHistory.save()

                whatsapp_url = send_whatsapp_message(phone_number=clientPhone, client_name=clientName, status=status)
                request.session['whatsapp_url'] = whatsapp_url
                messages.success(request, "DSC updated successfully.")

                return HttpResponseRedirect(reverse('listDSC'))
            else:
                messages.error(request, "Company not found.")
                return redirect(request.path)

    
    return render(request, 'dsc/addDSC.html', context)

def addCompany(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    groups = UpdatedGroup.objects.filter(subAdminID=user.subAdminID).all()
    context = {
        'base': base,
        'groups': groups,
        'user': user
    }

    if request.method == 'POST':
        groupName = request.POST.get('groupName')
        companyName = request.POST.get('companyName')

        if not groupName or not companyName:
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)
        else:
            subAdminID = user.subAdminID
            group = UpdatedGroup.objects.filter(groupName=groupName, subAdminID=subAdminID).first()

            if group:
                # Normalize the company name for case-insensitive comparison
                companyName_normalized = companyName.lower()

                if UpdatedCompany.objects.filter(companyName__iexact=companyName_normalized, groupID=group.groupID, subAdminID=subAdminID).exists():
                    messages.error(request, "Company already exists.")
                    return redirect(request.path)
                else:
                    company = UpdatedCompany(
                        companyName=companyName, groupID=group, userID=user, subAdminID=subAdminID
                    )
                    company.save()

                    companyHistory = HistoryCompany(
                        companyID=company, companyName=companyName, groupID=group,
                        userID=user, subAdminID=subAdminID, companyModifiedDate=company.companyModifiedDate
                    )
                    companyHistory.save()

                    messages.success(request, "Company added successfully.")
                    return HttpResponseRedirect(reverse('listCompany'))
            else:
                messages.error(request, "Group not found.")
                return redirect(request.path)

    
    return render(request, 'company/addCompany.html', context)

def addGroup(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    context = {
        'base': base,
        'user': user
    }
    if request.method == 'POST':
        groupName = request.POST.get('groupName')

        if not groupName:
            messages.error(request, "Group name cannot be empty.")
            return redirect(request.path)
        else:
            if user:
                subAdminID = user.subAdminID
                # Normalize the group name to make it case-insensitive
                groupName_normalized = groupName.lower()
                if UpdatedGroup.objects.filter(groupName__iexact=groupName_normalized, subAdminID=subAdminID).exists():
                    messages.error(request, "Group already exists.")
                    return redirect(request.path)
                else:
                    group = UpdatedGroup(
                        groupName=groupName, userID=user, subAdminID=subAdminID
                    )
                    group.save()

                    groupHistory = HistoryGroup(
                        groupID=group, groupName=groupName, userID=user,
                        subAdminID=subAdminID, groupModifiedDate=group.groupModifiedDate
                    )
                    groupHistory.save()
                    messages.success(request, "Group added successfully.")
                    return HttpResponseRedirect(reverse('listGroup'))

    
    return render(request, 'group/addGroup.html', context)

def addClient(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    # Fetch companies that do not have a client associated with them
    companies_with_no_clients = UpdatedCompany.objects.filter(
        subAdminID=user.subAdminID
    ).exclude(
        updatedclient__isnull=False
    )
    context = {
        'base': base,
        'companies': companies_with_no_clients
    }

    if request.method == 'POST':
        clientName = request.POST.get('clientName')
        companyName = request.POST.get('companyName')
        clientPhone = request.POST.get('clientPhone')

        # Check if all fields are filled
        if not all([clientName, companyName, clientPhone]):
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)

        if not re.match(r'^[A-Za-z\s]+$', clientName):
            messages.error(request, "Client name can only contain letters and spaces.")
            return redirect(request.path)

        # 2. Phone number validation: exactly 10 digits
        if not re.match(r'^\d{10}$', clientPhone):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect(request.path)

        # Check if phone number or email already exists
        subAdminID = user.subAdminID
        company = UpdatedCompany.objects.filter(companyName=companyName, subAdminID=subAdminID).first()

        if company:
            if UpdatedClient.objects.filter(clientPhone=clientPhone).exists():
                messages.error(request, "Phone number already exists.")
                return redirect(request.path)
            else:
                # Create and save the new client
                client = UpdatedClient(
                    clientName=clientName, companyID=company, userID=user,
                    clientPhone=clientPhone, subAdminID=subAdminID
                )
                client.save()

                # Save the client to the history
                clientHistory = HistoryClient(
                    clientID=client, clientName=clientName, companyID=company,
                    userID=user, clientPhone=clientPhone,
                    subAdminID=subAdminID, clientModifiedDate=client.clientModifiedDate
                )
                clientHistory.save()

                messages.success(request, "Client added successfully.")
                return HttpResponseRedirect(reverse('listClient'))
        else:
            messages.error(request, "Company not found.")
            return redirect(request.path)

    return render(request, 'client/addClient.html', context)


# All Update Function are here
def updateDSC(request, dscID):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    companies = UpdatedCompany.objects.filter(subAdminID=user.subAdminID).all()
    dsc = UpdatedDSC.objects.filter(subAdminID=user.subAdminID, dscID=dscID).first()
    dscHistory = HistoryDSC.objects.filter(subAdminID=user.subAdminID, dscID=dscID).all().order_by('-modifiedDate')
    client = UpdatedClient.objects.get(companyID=dsc.companyID)
    context = {
        'base': base,
        'dsc': dsc,
        'dscHistory': dscHistory,
        'user': user,
        'client': client,
        'companies': companies,
        'options': ['IN', 'OUT']
    }
    if request.method == 'POST':
        clientName = request.POST.get('clientName')
        companyName = request.POST.get('companyName')
        status = request.POST.get('status')
        location = request.POST.get('location')
        renewalDate = request.POST.get('renewalDate')
        receivedBy = request.POST.get('receivedBy', '')
        receivedFrom = request.POST.get('receivedFrom', '')
        clientPhone = request.POST.get('clientPhone')
        deliveredTo = request.POST.get('deliveredTo', '')

        if not all([clientName, companyName, status, location, renewalDate]):
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)
        else:
            if user:
                company = UpdatedCompany.objects.filter(companyName=companyName, subAdminID=user.subAdminID).first()
                
                if company:
                    dsc.clientName = clientName
                    dsc.companyID = company
                    dsc.status = status
                    dsc.location = location
                    dsc.renewalDate = renewalDate
                    dsc.receivedBy = receivedBy
                    dsc.receivedFrom = receivedFrom
                    dsc.deliveredTo = deliveredTo
                    dsc.clientPhone = clientPhone
                    dsc.userID = user
                    dsc.save()

                    dscHistory = HistoryDSC(
                        dscID=dsc,  clientName=clientName,  companyID=company,  status=status,  receivedBy=receivedBy, receivedFrom=receivedFrom,  deliveredTo=deliveredTo,  location=location,  renewalDate=renewalDate, clientPhone=clientPhone,  userID=user, subAdminID=user.subAdminID,
                        modifiedDate=dsc.modifiedDate
                    )
                    dscHistory.save()

                    whatsapp_url = send_whatsapp_message(phone_number=clientPhone, client_name=clientName, status=status)
                    messages.success(request, "DSC updated successfully.")
                    context['whatsurl'] = whatsapp_url
                    return render(request, 'dsc/updateDSC.html', context)
                else:
                    messages.error(request, "Company not found.")
                    return redirect(request.path)
                
    return render(request, 'dsc/updateDSC.html', context)
    
def updateCompany(request, companyID):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    company = UpdatedCompany.objects.get(companyID=companyID)
    companyHistory = HistoryCompany.objects.filter(companyID=companyID).all().order_by('-companyModifiedDate')
    groups = UpdatedGroup.objects.filter(subAdminID=user.subAdminID).all()
    context = {
        'base': base,
        'company': company,
        'groups': groups,
        'companyHistory': companyHistory,
        'user': user
    }
    if request.method == 'POST':
        groupName = request.POST.get('groupName')
        companyName = request.POST.get('companyName')
        
        if not groupName or not companyName:
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)
        else:
            if user:
                
                group = UpdatedGroup.objects.filter(groupName=groupName, subAdminID=user.subAdminID).first()

                if group:
                    companyName_normalized = companyName.lower()
                    if UpdatedCompany.objects.filter(companyName__iexact=companyName_normalized).exists():
                        messages.error(request, "Company already exists.")
                        return redirect(request.path)
                    else:
                        company.companyName = companyName
                        company.groupID = group
                        company.userID = user
                        company.save()

                        companyHistory = HistoryCompany(
                            companyID=company, companyName=companyName, groupID=group,
                            userID=user, subAdminID=user.subAdminID, companyModifiedDate=company.companyModifiedDate
                        )
                        companyHistory.save()

                        messages.success(request, "Company updated successfully.")
                        return redirect(request.path)
                else:
                    messages.error(request, "Group not found.")
                    return redirect(request.path)
                
    return render(request, 'company/updateCompany.html', context)
    
def updateGroup(request, groupID):
    user = getUser(request).get('user')
    base = getUser(request).get('base')
            
    group = UpdatedGroup.objects.get(groupID=groupID)
    groupHistory = HistoryGroup.objects.filter(groupID=groupID).all().order_by('-groupModifiedDate')
    context = {
        'base': base,
        'group': group,
        'user': user,
        'groupHistory': groupHistory
    }

    if request.method == 'POST':
        groupName = request.POST.get('groupName')
        
        if not groupName:
            messages.error(request, "Group name cannot be empty.")
            return redirect(request.path)
        else:
            if user:
                groupName_normalized = groupName.lower()
                # Check if the group already exists with the new name
                if UpdatedGroup.objects.filter(groupName__iexact=groupName_normalized).exists():
                    messages.error(request, "Group already exists.")
                    return redirect(request.path)
                
                group.groupName = groupName
                group.userID = user
                group.subAdminID = user.subAdminID
                group.save()

                groupHistory = HistoryGroup(
                    groupID=group, groupName=groupName, userID=user,
                    subAdminID=user.subAdminID, groupModifiedDate=group.groupModifiedDate
                )
                groupHistory.save()

                messages.success(request, "Group updated successfully.")
                return redirect(request.path)

    return render(request, 'group/updateGroup.html', context)
    
def updateClient(request, clientID):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    client = UpdatedClient.objects.get(clientID=clientID)
    clientHistory = HistoryClient.objects.filter(clientID=clientID).all().order_by('-clientModifiedDate')
    
    context = {
        'base': base,
        'client': client,
        'clientHistory': clientHistory,
        'user': user
    }

    if request.method == 'POST':
        clientName = request.POST.get('clientName')
        clientPhone = request.POST.get('clientPhone')

        # Check if all fields are filled
        if not all([clientName, clientPhone]):
            messages.error(request, "Please fill all required fields.")
            return redirect(request.path)

        # 1. Name validation: only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', clientName):
            messages.error(request, "Client name can only contain letters and spaces.")
            return redirect(request.path)

        # 2. Phone number validation: exactly 10 digits
        if not re.match(r'^\d{10}$', clientPhone):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect(request.path)

        if user:
            if client:
                # Check if the phone number or email already exists
                if UpdatedClient.objects.filter(clientPhone=clientPhone).exists() and UpdatedClient.objects.filter(clientName=clientName).exists():
                    messages.error(request, "Phone number already exists.")
                    return redirect(request.path)

                # Update client details
                client.clientName = clientName
                client.userID = user
                client.clientPhone = clientPhone
                client.save()

                # Update client history
                clientHistory = HistoryClient(
                    clientID=client, clientName=clientName, companyID=client.companyID,
                    userID=user, clientPhone=clientPhone,
                    subAdminID=user.subAdminID, clientModifiedDate=client.clientModifiedDate
                )
                clientHistory.save()

                messages.success(request, "Client updated successfully.")
                return redirect(request.path)
            else:
                messages.error(request, "Company not found.")
                return redirect(request.path)

    return render(request, 'client/updateClient.html', context)


# All Delete Function are here
def deleteDSC(request):
    if request.method == 'POST':
        dscIDs = request.POST.getlist('dscIDs')
        if not dscIDs:
            messages.error(request, "No DSCs selected for deletion.")
        else:
            count, _ = UpdatedDSC.objects.filter(dscID__in=dscIDs).delete()
            if count > 0:
                messages.success(request, f"Deleted DSC(s) successfully.")
            else:
                messages.error(request, "No DSCs were deleted. Please try again.")
    
    return redirect('listDSC')

def deleteCompany(request):
    if request.method == 'POST':
        companyIDs = request.POST.getlist('companyIDs')
        if not companyIDs:
            messages.error(request, "No companies selected for deletion.")
        else:
            count, _ = UpdatedCompany.objects.filter(companyID__in=companyIDs).delete()
            if count > 0:
                messages.success(request, f"Deleted company(ies) successfully.")
            else:
                messages.error(request, "No companies were deleted. Please try again.")
    
    return redirect('listCompany')

def deleteGroup(request):
    if request.method == 'POST':
        groupIDs = request.POST.getlist('groupIDs')
        if not groupIDs:
            messages.error(request, "No groups selected for deletion.")
        else:
            count, _ = UpdatedGroup.objects.filter(groupID__in=groupIDs).delete()
            if count > 0:
                messages.success(request, f"Selected group(s) deleted successfully.")
            else:
                messages.error(request, "No groups were deleted. Please try again.")
    
    return redirect('listGroup')

def deleteClient(request):
    if request.method == 'POST':
        clientIDs = request.POST.getlist('clientIDs')
        if not clientIDs:
            messages.error(request, "No clients selected for deletion.")
        else:
            count, _ = UpdatedClient.objects.filter(clientID__in=clientIDs).delete()
            if count > 0:
                messages.success(request, f"Deleted client(s) successfully.")
            else:
                messages.error(request, "No clients were deleted. Please try again.")

    return redirect('listClient')


def updatePassword(request):
    user = getUser(request).get('user')
    subAdmin = getUser(request).get('subAdmin')
    superAdmin = getUser(request).get('superAdmin')
    base = getUser(request).get('base')
    
    if subAdmin:
        user = None

    if request.method == 'POST':
        oldPassword = request.POST.get('oldPassword')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')

        # Password validation function
        def validate_new_password(password):
            return (len(password) >= 8 and
                    re.search(r'[A-Za-z]', password) and
                    re.search(r'\d', password) and
                    re.search(r'[@$!%*?&#]', password))

        # Check if it's a user or subAdmin updating their password
        if user:
            if check_password(oldPassword, user.userPassword):
                if newPassword == confirmPassword:
                    if validate_new_password(newPassword):
                        user.userPassword = make_password(newPassword)
                        user.save()
                        messages.success(request, 'Password updated successfully!')
                    else:
                        messages.error(request, "New password must be at least 8 characters long and contain letters, numbers, and special characters (@, $, !, %, *, ?, &, #).")
                else:
                    messages.error(request, 'New password and confirmation do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        elif subAdmin:
            if check_password(oldPassword, subAdmin.subAdminPassword):
                print(subAdmin.subAdminPassword)
                if newPassword == confirmPassword:
                    if validate_new_password(newPassword):
                        subAdmin.subAdminPassword = make_password(newPassword)
                        subAdmin.save()
                        messages.success(request, 'Password updated successfully!')
                    else:
                        messages.error(request, "New password must be at least 8 characters long and contain letters, numbers, and special characters (@, $, !, %, *, ?, &, #).")
                else:
                    messages.error(request, 'New password and confirmation do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        elif superAdmin:
            if check_password(oldPassword, superAdmin.superAdminPassword):
                if newPassword == confirmPassword:
                    if validate_new_password(newPassword):
                        superAdmin.superAdminPassword = make_password(newPassword)
                        superAdmin.save()
                        messages.success(request, 'Password updated successfully!')
                    else:
                        messages.error(request, "New password must be at least 8 characters long and contain letters, numbers, and special characters (@, $, !, %, *, ?, &, #).")
                else:
                    messages.error(request, 'New password and confirmation do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')

    context = {
        'base': base,
        'subAdmin': subAdmin
    }
    return render(request, 'password/updatePassword.html', context)


def feedBack(request):
    user = getUser(request).get('user')
    base = getUser(request).get('base')

    context = {
        'base': base,
        'user': user,
    }
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedbackText = request.POST.get('feedBack')

        Feedback.objects.create(rating=rating, feedbackText=feedbackText, subAdminID=user.subAdminID)
        messages.success(request, "Your feedback is submited successfully.")
        return redirect(request.path) 

    return render(request, 'contactUs/feedBack.html', context)


def fetchGroupName(request):
    if request.method == 'POST':
        companyName = request.POST.get('companyName')  # Corrected typo
        user = getUser(request).get('user')

        subAdminID = user.subAdminID

        try:
            company = UpdatedCompany.objects.get(companyName=companyName, subAdminID=subAdminID)
            groupName = company.groupID.groupName
            
            try: 
                client = UpdatedClient.objects.get(subAdminID=subAdminID, companyID=company.companyID)
                clientName = client.clientName
                clientPhone = client.clientPhone
            except:
                clientName = ''
                clientPhone = ''

            response_data = {
                'status': 'success',
                'group_name': groupName,
                'client_name': clientName,
                'client_phone': clientPhone,  
                'exists': True
            }
        except UpdatedCompany.DoesNotExist:
            response_data = {
                'status': 'error',
                'message': 'Company name does not exist',
                'exists': False
            }
        
        return JsonResponse(response_data)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



import urllib.parse
def send_whatsapp_message(phone_number, client_name, status):
    # Clean the phone number (remove spaces and '+' signs)
    phone_number = phone_number.replace('+', '').replace(' ', '')
    
    # Create the message
    message = f"Hello {client_name}, your DSC status is {status}."
    
    # URL encode the message
    encoded_message = urllib.parse.quote(message)
    
    # Generate the WhatsApp URL
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
    
    # Return the WhatsApp URL to be used in the frontend or backend
    return whatsapp_url

