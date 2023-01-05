import pandas as pd

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def get_stats(youtube, video_id):

    r = youtube.videos().list(
        part="statistics,contentDetails",
        id=video_id,
        fields="items(statistics," + "contentDetails(duration))"
    ).execute()
    
    info = {}
    try:
        duration = r['items'][0]['contentDetails']['duration']
        views = r['items'][0]['statistics']['viewCount']
        likes = r['items'][0]['statistics']['likeCount']
        favorites = r['items'][0]['statistics']['favoriteCount']
        comments = r['items'][0]['statistics']['commentCount']
        info['id'] = video_id
        info['duration'] = duration
        info['views'] = views
        info['likes'] = likes
        info['favorites'] = favorites
        info['comments'] = comments
    except Exception as e:
        print(e)
        print('NOOOOOO!')
    
    return info


def get_potential_videos(youtube, querystring):
    request = youtube.search().list(
        part="id,snippet",
        channelId="UCdoadna9HFHsxXWhafhNvKw",
        type='video',
        q=querystring,
        maxResults=2,
        fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))",
    )
    response = request.execute()

    potential_videos = {}

    return response




def get_youtube_info(youtube, title_with_section, section):
    #title_with_section = "Building next-gen applications with event-driven architectures (API311-R)"
    #section = 'API311-R'

    response = get_potential_videos(youtube, title_with_section)
    #print(response)

    potential_videos = response['items']
    filtered_potential_videos = [ {
        'video_id': pv['id']['videoId'],
        'res_title': pv['snippet']['title']
            }
            for pv in potential_videos
            if section in pv['snippet']['title']]

    if len(filtered_potential_videos) > 1:
        print('MORE THAN ONE!')
        print('will take the first one')
    elif len(filtered_potential_videos) < 1:
        print('empty? dont know what to do here')
        #will have to raise anyway raise MyException('welp')
        return {} # see if that works

    else:
        print('ok')



    target_vid = filtered_potential_videos[0]
    info = get_stats(youtube, target_vid['video_id'])
    #  could get all stats and sum up the metrics
    #filtered_potential_videos[0]['views'] = sum([ info['views'] for info in filtered_potential_videos])
    #filtered_potential_videos[0]['likes'] = sum([ info['likes'] for info in filtered_potential_videos])
    #filtered_potential_videos[0]['favorites'] = sum([ info['favorites'] for info in filtered_potential_videos])
    #filtered_potential_videos[0]['comments'] = sum([ info['comments'] for info in filtered_potential_videos])
    #print(info)
    return {**target_vid, **info}










def main():


    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


    # subselect
    teams = [
        #'Apps',
        #'infra',
        #'security',
        #'HPC',
        #'management',
        #'SAP',
        'BDT',
        'nerds',
        ]


    # read data
    df = pd.read_excel('sessions.xlsx')
    print(f'filter to just {teams}')
    df = df[df.teams.isin(teams)]
    print(df)
    

    
    # invoke api
    youtube_data = {}
    try:
        for i, row in df.iterrows():
            result = get_youtube_info(youtube, row['title_with_section'], row['section'])
            youtube_data.update({i: result})
    except Exception as e:
        print(e)
        print('ran out of juice here')

    # stitch back and save
    enriched = pd.DataFrame(youtube_data).T
    print(enriched)
    final = df.join(enriched).assign(link=lambda x: 'https://www.youtube.com/watch?v=' + x.video_id)
    final.to_excel('out.xlsx')


if __name__ == "__main__":
    main()


