# b2c_operations.py

import requests

def process_b2c_payment(user):
    try:
        # Check if the user has more than 1000 points
        if user.points >= 1000:
            # Check if the user's community has an organization
            if user.community and user.community.community_roganaization.exists():
                organization = user.community.community_roganaization.first()
                points_to_award = (user.points // 1000) * 100
                user.points = user.points % 1000

                # Dummy implementation for initiating payment through user's phone
                payment_payload = {
                    'consumer_key': organization.consumer_key,
                    'consumer_secret': organization.consumer_secret,
                    # 'shortcode': organization.shortcode,
                    'amount': points_to_award,
                    'phone_number': user.contact_number
                }

                # Replace this URL with the actual payment API endpoint
                payment_url = "https://example-payment-api.com/initiate_payment"
                response = requests.post(payment_url, data=payment_payload)

                if response.status_code == 200:
                    user.save()  # Save the user's updated points
                    print(f"Payment of {points_to_award} shillings initiated for user {user.email}")
                else:
                    print(f"Failed to initiate payment for user {user.email}: {response.text}")
            else:
                print(f"User {user.email} belongs to a community without an organization.")
        else:
            print(f"User {user.email} does not have enough points for a payment.")
    except Exception as e:
        print(f"Error processing B2C payment for user {user.email}: {str(e)}")
