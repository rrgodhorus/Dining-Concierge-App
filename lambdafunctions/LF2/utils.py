def get_restaurants_data_formatted(restaurants):
    return [
        f"{restaurant['name']['S']}, located at {restaurant['address']['S']}, with rating {restaurant['rating']['N']}"
        
        for restaurant in restaurants
    ]

def create_email_payload(restaurants, cuisine, number_of_people, dining_date, dining_time):
    restaurants = get_restaurants_data_formatted(restaurants)
    subject = "Dining Concierge App: Recommendations"

    body_text = f"""
    Hello!
    Here are my {cuisine} restaurant suggestions for {number_of_people} people, for {dining_date} at {dining_time} :
    {"\n".join([f"- {restaurant}" for restaurant in restaurants])}

    Enjoy your meal!
    """
    body_html = f"""
    <html>
    <head></head>
    <body>
      <h3>Hello!</h3>
      <p>Here are my {cuisine} restaurant suggestions for {number_of_people} people, for {dining_date} at {dining_time} :</p>
      <ol>
        {"\n".join([f"<li>{restaurant}</li>" for restaurant in restaurants])}
      </ol>
      <p>Enjoy your meal!</p>
    </body>
    </html>
    """

    # Create the email message
    message = {
        'Subject': {
            'Data': subject
        },
        'Body': {
            'Text': {
                'Data': body_text
            },
            'Html': {
                'Data': body_html
            }
        }
    }
    return message

