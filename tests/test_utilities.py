from get_to_the_gig import utilities


def test__load_js_dict():
    script = """var thisShow = {
  eventID: '44179',
  eventTitle: '08-10-2024 Gazebo Effect',
  dateandTime: '08/10/2024 8:00 pm',
  doorTime: '7:00 pm',
  showImageURL: 'https://d1ct6yhiw4gple.cloudfront.net/wp-content/uploads/2024/05/08-10-24-gazebo-effect.png',
  eventVenueName: 'Lincoln Hall',
  eventGenre: '',
  externalLink: ''
};"""
    assert utilities.load_js_dict(script) == {
        "eventID": "44179",
        "eventTitle": "08-10-2024 Gazebo Effect",
        "dateandTime": "08/10/2024 8:00 pm",
        "doorTime": "7:00 pm",
        "showImageURL": "https://d1ct6yhiw4gple.cloudfront.net/wp-content/uploads/2024/05/08-10-24-gazebo-effect.png",
        "eventVenueName": "Lincoln Hall",
        "eventGenre": "",
        "externalLink": "",
    }
