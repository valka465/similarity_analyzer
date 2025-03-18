import streamlit as st
import requests
import pandas as pd
import holoviews as hv
from collections import defaultdict, Counter
import seaborn as sns
from bokeh.embed import file_html
from bokeh.resources import CDN
import streamlit.components.v1 as components
import pyperclip

hv.extension('bokeh')

def copy_to_clipboard(js_id, text):
    js_code = f"""
    <script>
    function copyText_{js_id}() {{
        navigator.clipboard.writeText(`{text}`).then(() => {{
            let btn = document.getElementById("copy_btn_{js_id}");
            let originalText = btn.innerHTML;
            btn.innerHTML = "Copied!";
            setTimeout(() => btn.innerHTML = originalText, 2000);
        }});
    }}
    </script>
    <button id="copy_btn_{js_id}" onclick="copyText_{js_id}()" 
        style="padding: 8px 12px; margin-top: 10px; background-color: #007bff; 
               color: white; border: none; border-radius: 6px; cursor: pointer;
               font-weight: bold; transition: background 0.3s ease;">
        Copy
    </button>
    """
    components.html(js_code, height=50)



st.set_page_config(page_title="Google Keyword Similarity Analyzer", layout="wide")

st.title("🔍 Google Keyword Similarity Analyzer")
st.write("Analyze the similarity of Google search queries with filtering by country and language")
    
api_key = st.text_input("Enter [HasData's](https://app.hasdata.com/sign-up&utm_source=streamlit) API key", type="password", 
                        help="Get your API key from HasData at [hasdata.com](https://app.hasdata.com/sign-up&utm_source=streamlit). It's free.")

countries = {
    "us": "United States","af": "Afghanistan", "al": "Albania", "dz": "Algeria", "as": "American Samoa",
    "ad": "Andorra","ao": "Angola","ai": "Anguilla","aq": "Antarctica",
    "ag": "Antigua and Barbuda","ar": "Argentina","am": "Armenia",
    "aw": "Aruba","au": "Australia","at": "Austria","az": "Azerbaijan",
    "bs": "Bahamas","bh": "Bahrain","bd": "Bangladesh","bb": "Barbados",
    "by": "Belarus","be": "Belgium","bz": "Belize","bj": "Benin",
    "bm": "Bermuda","bt": "Bhutan","bo": "Bolivia","ba": "Bosnia and Herzegovina",
    "bw": "Botswana","bv": "Bouvet Island","br": "Brazil","io": "British Indian Ocean Territory",
    "bn": "Brunei Darussalam","bg": "Bulgaria","bf": "Burkina Faso",
    "bi": "Burundi","kh": "Cambodia","cm": "Cameroon","ca": "Canada",
    "cv": "Cape Verde","ky": "Cayman Islands","cf": "Central African Republic",
    "td": "Chad","cl": "Chile","cn": "China","cx": "Christmas Island","cc": "Cocos (Keeling) Islands",
    "co": "Colombia","km": "Comoros","cg": "Congo","cd": "Congo, the Democratic Republic of the",
    "ck": "Cook Islands","cr": "Costa Rica","ci": "Cote D'ivoire","hr": "Croatia",
    "cu": "Cuba","cy": "Cyprus","cz": "Czech Republic","dk": "Denmark",
    "dj": "Djibouti","dm": "Dominica","do": "Dominican Republic","ec": "Ecuador",
    "eg": "Egypt","sv": "El Salvador","gq": "Equatorial Guinea","er": "Eritrea",
    "ee": "Estonia","et": "Ethiopia","fk": "Falkland Islands (Malvinas)",
    "fo": "Faroe Islands","fj": "Fiji","fi": "Finland","fr": "France",
    "gf": "French Guiana","pf": "French Polynesia",
    "tf": "French Southern Territories","ga": "Gabon","gm": "Gambia",
    "ge": "Georgia","de": "Germany","gh": "Ghana","gi": "Gibraltar",
    "gr": "Greece","gl": "Greenland","gd": "Grenada","gp": "Guadeloupe",
    "gu": "Guam","gt": "Guatemala","gn": "Guinea","gw": "Guinea-Bissau",
    "gy": "Guyana","ht": "Haiti","hm": "Heard Island and Mcdonald Islands",
    "va": "Holy See (Vatican City State)","hn": "Honduras","hk": "Hong Kong",
    "hu": "Hungary","is": "Iceland","in": "India","id": "Indonesia",
    "ir": "Iran, Islamic Republic of","iq": "Iraq","ie": "Ireland",
    "il": "Israel","it": "Italy","jm": "Jamaica","jp": "Japan",
    "jo": "Jordan","kz": "Kazakhstan","ke": "Kenya","ki": "Kiribati",
    "kp": "Korea, Democratic People's Republic of","kr": "Korea, Republic of","kw": "Kuwait",
    "kg": "Kyrgyzstan","la": "Lao People's Democratic Republic",
    "lv": "Latvia","lb": "Lebanon","ls": "Lesotho","lr": "Liberia",
    "ly": "Libyan Arab Jamahiriya","li": "Liechtenstein","lt": "Lithuania","lu": "Luxembourg",
    "mo": "Macao","mk": "Macedonia, the Former Yugoslav Republic of",
    "mg": "Madagascar","mw": "Malawi","my": "Malaysia","mv": "Maldives",
    "ml": "Mali","mt": "Malta","mh": "Marshall Islands","mq": "Martinique",
    "mr": "Mauritania","mu": "Mauritius","yt": "Mayotte","mx": "Mexico",
    "fm": "Micronesia, Federated States of","md": "Moldova, Republic of",
    "mc": "Monaco","mn": "Mongolia","ms": "Montserrat","ma": "Morocco",
    "mz": "Mozambique","mm": "Myanmar","na": "Namibia","nr": "Nauru",
    "np": "Nepal","nl": "Netherlands","nz": "New Zealand","ni": "Nicaragua",
    "ne": "Niger","ng": "Nigeria","nu": "Niue","nf": "Norfolk Island",
    "mp": "Northern Mariana Islands","no": "Norway","om": "Oman",
    "pk": "Pakistan","pw": "Palau","pa": "Panama","pg": "Papua New Guinea",
    "py": "Paraguay","pe": "Peru","ph": "Philippines","pl": "Poland",
    "pt": "Portugal","pr": "Puerto Rico",
    "qa": "Qatar","ro": "Romania","ru": "Russian Federation","rw": "Rwanda"
}

languages = {
    "en": "English","af": "Afrikaans","ak": "Akan","sq": "Albanian","ws": "Samoa",
    "am": "Amharic","ar": "Arabic","hy": "Armenian","az": "Azerbaijani",
    "eu": "Basque","be": "Belarusian","bem": "Bemba","bn": "Bengali",
    "bh": "Bihari","bs": "Bosnian","br": "Breton","bg": "Bulgarian",
    "bt": "Bhutanese","km": "Cambodian","ca": "Catalan","chr": "Cherokee",
    "ny": "Chichewa","zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)","co": "Corsican","hr": "Croatian",
    "cs": "Czech","da": "Danish","nl": "Dutch",
    "eo": "Esperanto","et": "Estonian","ee": "Ewe","fo": "Faroese",
    "tl": "Filipino","fi": "Finnish","fr": "French","fy": "Frisian",
    "gaa": "Ga","gl": "Galician","ka": "Georgian","de": "German",
    "el": "Greek","kl": "Greenlandic","gn": "Guarani","gu": "Gujarati",
    "ht": "Haitian Creole","ha": "Hausa","haw": "Hawaiian",
    "iw": "Hebrew","hi": "Hindi","hu": "Hungarian","is": "Icelandic",
    "ig": "Igbo","id": "Indonesian","ia": "Interlingua","ga": "Irish",
    "it": "Italian","ja": "Japanese","jw": "Javanese","kn": "Kannada",
    "kk": "Kazakh","rw": "Kinyarwanda","rn": "Kirundi","kg": "Kongo",
    "ko": "Korean","ku": "Kurdish","ckb": "Kurdish (Soranî)","ky": "Kyrgyz",
    "lo": "Laothian","la": "Latin","lv": "Latvian","ln": "Lingala",
    "lt": "Lithuanian","loz": "Lozi","lg": "Luganda","ach": "Luo",
    "mk": "Macedonian","mg": "Malagasy","my": "Malay","ml": "Malayalam",
    "mt": "Maltese","mv": "Maldives","mi": "Maori","mr": "Marathi",
    "mfe": "Mauritian Creole","mo": "Moldavian","mn": "Mongolian","sr-me": "Montenegrin",
    "ne": "Nepali","pcm": "Nigerian Pidgin","nso": "Northern Sotho","no": "Norwegian",
    "nn": "Norwegian (Nynorsk)","oc": "Occitan","or": "Oriya",
    "om": "Oromo","ps": "Pashto","fa": "Persian","pl": "Polish",
    "pt": "Portuguese","pt-br": "Portuguese (Brazil)","pt-pt": "Portuguese (Portugal)",
    "pa": "Punjabi","qu": "Quechua","ro": "Romanian","rm": "Romansh",
    "nyn": "Runyakitara","ru": "Russian","gd": "Scots Gaelic","sr": "Serbian",
    "sh": "Serbo-Croatian","st": "Sesotho","tn": "Setswana","crs": "Seychellois Creole",
    "sn": "Shona","sd": "Sindhi","si": "Sinhalese","sk": "Slovak",
    "sl": "Slovenian","so": "Somali","es": "Spanish","es-419": "Spanish (Latin American)",
    "su": "Sundanese","sw": "Swahili","sv": "Swedish","tg": "Tajik",
    "ta": "Tamil","tt": "Tatar","te": "Telugu","th": "Thai",
    "ti": "Tigrinya","to": "Tonga","lua": "Tshiluba","tum": "Tumbuka",
    "tr": "Turkish","tk": "Turkmen","tw": "Twi","ug": "Uighur",
    "uk": "Ukrainian","ur": "Urdu","uz": "Uzbek","vu": "Vanuatu",
    "vi": "Vietnamese","cy": "Welsh","wo": "Wolof","xh": "Xhosa",
    "yi": "Yiddish","yo": "Yoruba","zu": "Zulu"
}

with st.form("search_form"):
    queries = st.text_area("Enter search queries (comma or newline separated)", 
                       placeholder="Enter keywords, for example: scraping, web scraping, python")


    country = st.selectbox("Select country", options=list(countries.keys()), format_func=lambda x: countries[x])
    language = st.selectbox("Select language", options=list(languages.keys()), format_func=lambda x: languages[x])
    num_res = st.slider("Number of results", min_value=10, max_value=25, value=10)
    search_button = st.form_submit_button("🔎 Search")

if "search_results" not in st.session_state:
    st.session_state.search_results = {}
    st.session_state.query_list = []

if search_button:
    if not api_key:
        st.error("Please enter an API key!")

    else:          
        base_url = "https://api.hasdata.com/scrape/google/serp"

        st.session_state.query_list = [q.strip() for q in queries.replace("\n", ",").split(",") if q.strip()]
        st.session_state.search_results = defaultdict(set)
        
        for query in st.session_state.query_list:
            params = {
                "q": query, "country": country,
                "language": language, "num_results": num_res
            }
            url = f"{base_url}?q={params['q']}&gl={params['country']}&hl={params['language']}&num={params['num_results']}"
            headers = {'Content-Type': 'application/json', 'x-request-source': 'streamlit_similarity', 'x-api-key': api_key}

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("organicResults", [])
                
                for result in results:
                    link = result.get('link', 'No link')
                    st.session_state.search_results[query].add(link)
                
all_links = [link for links in st.session_state.search_results.values() for link in links]
link_counts = Counter(all_links)
sorted_links = sorted(link_counts.items(), key=lambda x: -x[1])

intersecting_links = {link for link, count in sorted_links if count > 1}
link_colors = {link: sns.color_palette("husl", len(intersecting_links))[i] for i, link in enumerate(intersecting_links)}

#Links
if st.session_state.query_list:
    st.subheader("📊 Query Links")
    num_columns = 3 
    columns = st.columns(num_columns, gap="small")
    
    query_groups = [st.session_state.query_list[i:i + num_columns] for i in range(0, len(st.session_state.query_list), num_columns)]
    
    for query_group in query_groups:
        columns = st.columns(len(query_group), gap="small")
        for idx, (query, col) in enumerate(zip(query_group, columns)):
            st.markdown("<br>", unsafe_allow_html=True)
            with col:
                
                query_links = sorted(st.session_state.search_results[query], key=lambda x: link_counts[x], reverse=True)
                link_text = "\n".join(query_links)
                
                col1, col2 = st.columns([2, 1]) 
                with col1:
                    st.markdown(f"### {query}")
                with col2:
                    copy_to_clipboard(f"copy_{idx}", link_text)

                for link in sorted(st.session_state.search_results[query], key=lambda x: link_counts[x], reverse=True):
                    color = ""
                    if link in intersecting_links:
                        rgb = link_colors[link]
                        color = f"background-color: rgba({int(rgb[0] * 255)}, {int(rgb[1] * 255)}, {int(rgb[2] * 255)}, 0.3);"
                    st.markdown(f"<div style='{color} padding: 5px; border-radius: 5px;'><a href='{link}' target='_blank' style='max-width: 90%; white-space: nowrap; overflow: hidden;text-overflow: ellipsis; display: inline-block;'>{link}</a></div>", unsafe_allow_html=True)


if st.session_state.query_list:
    st.markdown("<br>", unsafe_allow_html=True)

    top_10_links = sorted_links[:10]
    top_10_text = "\n".join([link for link, count in top_10_links])

    col3, col4 = st.columns([2, 1]) 
    with col3:
        st.subheader("📊 Most Frequent Links")
        
    with col4:
        copy_to_clipboard("copy_top_10", top_10_text)

    for link, count in top_10_links:
        if link in link_colors: 
            rgb = link_colors[link]
            bg_color = f"rgba({int(rgb[0] * 255)}, {int(rgb[1] * 255)}, {int(rgb[2] * 255)}, 0.3)"
        else:
            bg_color = ""
            
        st.markdown(f"""<div style='padding: 5px; max-width: 91.5%; border-radius: 5px; font-weight: bold; background-color: {bg_color}; padding: 8px; margin: 5px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                            <span style='color: #ff5733; font-size: 16px; margin-right: 8px;'>{count}</span>
                            <a href='{link}' target='_blank' style='text-decoration: none; font-weight: bold; color: #007bff; max-width: 90%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: inline-block;'>{link}</a>
                        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

## Graph
if len(st.session_state.query_list) > 1:
    st.subheader("📊 Interactive Analysis of Intersections")

    intersections = defaultdict(Counter)

    for query, links in st.session_state.search_results.items():
        for other_query, other_links in st.session_state.search_results.items():
            if query != other_query:
                intersection_count = len(links & other_links) 
                if intersection_count > 0:
                    intersections[query][other_query] = intersection_count

    col1, col2 = st.columns([2, 1])  

    with col2:
        st.subheader("Select Queries")
        selected_queries = []
        
        for query in st.session_state.query_list:
            if st.checkbox(query, value=True):
                selected_queries.append(query)


    filtered_chord_data = []
    common_links = None

    for query in selected_queries:
        if query in intersections:
            for other_query, count in intersections[query].items():
                if other_query in selected_queries:
                    filtered_chord_data.append((query, other_query, count))

    if selected_queries:
        common_links = st.session_state.search_results[selected_queries[0]].copy()
        for query in selected_queries[1:]:
            common_links &= st.session_state.search_results[query]

    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        filtered_chord_data = []
        seen_pairs = set()

        for query in selected_queries:
            if query in intersections:
                for other_query, count in intersections[query].items():
                    if other_query in selected_queries:
                        pair = tuple(sorted([query, other_query]))  
                        if pair not in seen_pairs:
                            filtered_chord_data.append((query, other_query, count+1))
                            seen_pairs.add(pair)
                            
        if len(selected_queries) > 1 and filtered_chord_data:
            edges = pd.DataFrame(filtered_chord_data, columns=['source', 'target', 'value'])
            nodes = pd.DataFrame({'name': selected_queries})

            chord = hv.Chord((edges, hv.Dataset(nodes, 'name')))
            chord = chord.opts(
                hv.opts.Chord(
                    cmap='Category10',
                    edge_color='value',
                    edge_cmap='viridis',
                    node_size=30,
                    edge_line_width=1, 
                    edge_alpha=0.85,
                    width=700, height=700,
                    labels='name',
                    node_color='name',
                )
            )

            bokeh_plot = hv.render(chord, backend='bokeh')
            html = file_html(bokeh_plot, CDN, "Chord Diagram")
            components.html(html, height=700)
        else:
            st.info("Select at least two queries to generate the chart.")

    with col2:
        
        query_links_copy = sorted(common_links)
        link_text_copy = "\n".join(query_links_copy)
        col3, col4 = st.columns([2, 1]) 
        with col3:
            st.subheader("Common Links for Selected Queries")
        with col4:
            copy_to_clipboard("link_text_copy", link_text_copy)   
        
    
        if common_links:
            total_links = len(st.session_state.search_results[selected_queries[0]]) 
            common_count = len(common_links)  
            similarity_percentage = (common_count / total_links) * 100 if total_links > 0 else 0

            st.write(f"🔄 Similarity Percentage: {similarity_percentage:.2f}%")

            for link in sorted(common_links):
                st.markdown(
                    f"""
                    <div style="background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; 
                                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                        <a href="{link}" target="_blank" title="{link}" 
                            style="text-decoration: none; font-weight: bold; color: #007bff; max-width: 90%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: inline-block;">{link}</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
        else:
            st.write("No links found for all selected queries.")
