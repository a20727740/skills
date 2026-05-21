#!/usr/bin/env python3
"""
Translate English to Irish (Gaeilge) for ga-IE.js locale file.
Reads the current file, replaces English values with Irish translations,
handles apostrophes by using double quotes for any Irish string containing '.
"""

import re

# Build comprehensive translation dictionary
# Organized by semantic groups for manageability

EN_TO_GA = {
    # === Common UI Strings ===
    "File Information": "Eolas Comhaid",
    "Open": "Oscail",
    "Close": "Dún",
    "Okay": "Ceart go Leor",
    "Confirm": "Deimhnigh",
    "Cancel": "Cealaigh",
    "Submit": "Cuir Isteach",
    "Save": "Sábháil",
    "Delete": "Scrios",
    "Edit": "Cuir in Eagar",
    "Add": "Cuir Leis",
    "Search": "Cuardaigh",
    "Reset": "Athshocraigh",
    "Loading...": "Ag Lódáil...",
    "Pull up to load more": "Tarraing aníos le haghaidh tuilleadh",
    "No more": "Níl tuilleadh ann",
    "No Data": "Níl Aon Sonraí",
    "Success": "D'éirigh Leis",
    "Failed": "Theip",
    "Error": "Earráid",
    "Warning": "Rabhadh",
    "Info": "Faisnéis",
    "Back": "Ar Ais",
    "Next": "Ar Aghaidh",
    "Previous": "Roimhe Seo",
    "Close": "Dún",
    "Open": "Oscail",
    "Yes": "Tá",
    "No": "Níl",
    "OK": "Ceart go Leor",
    "Upgrade": "Uasghrádaigh",
    "Month": "Mí",
    "Year": "Bliain",
    "Day": "Lá",
    "Today": "Inniu",
    "Metal": "Miotal",
    "Wood": "Adhmad",
    "Water": "Uisce",
    "Fire": "Tine",
    "Earth": "Talamh",
    "Career": "Gairm",
    "Wealth": "Saibhreas",
    "Relationship": "Caidreamh",
    "Health": "Sláinte",
    "Studies": "Staidéar",
    "Emotion": "Mothúchán",
    "January": "Eanáir",
    "February": "Feabhra",
    "March": "Márta",
    "April": "Aibreán",
    "May": "Bealtaine",
    "June": "Meitheamh",
    "July": "Iúil",
    "August": "Lúnasa",
    "September": "Meán Fómhair",
    "October": "Deireadh Fómhair",
    "November": "Samhain",
    "December": "Nollaig",
    "Jan": "Ean",
    "Feb": "Fea",
    "Mar": "Már",
    "Apr": "Aib",
    "May": "Beal",
    "Jun": "Mei",
    "Jul": "Iú",
    "Aug": "Lún",
    "Sep": "MFóm",
    "Oct": "DFóm",
    "Nov": "Samh",
    "Dec": "Noll",
    "Take Photo": "Glac Grianghraf",
    "Choose from Album": "Roghnaigh ó Albam",
    "Select from Files": "Roghnaigh ó Chomhaid",
    "Uploading...": "Ag Uaslódáil...",
    "Upload Successful": "Uaslódáil Rathúil",
    "Upload Failed": "Uaslódáil Ar Theip",
    "Calculating File MD5": "Ag Ríomh MD5 an Chomhaid",
    "Getting Upload URL": "Ag Fáil URL Uaslódála",
    "Uploading File to OSS": "Ag Uaslódáil Comhad chuig OSS",
    "Saving File Information": "Ag Sábháil Eolais an Chomhaid",
    "Upload Complete": "Uaslódáil Críochnaithe",
    "Failed to Read File": "Theip ar an gComhad a Léamh",
    "Failed to Get Upload URL": "Theip ar URL Uaslódála a Fháil",
    "Upload URL Information Incomplete": "Faisnéis URL Uaslódála Neamhchomhlánaithe",
    "Failed to Save File Information": "Theip ar Fhaisnéis an Chomhaid a Shábháil",
    "Media ID Not Found": "Níor Fuarthas Aitheantas na Meán",
    "Permission Denied": "Cead Diúltaithe",
    "User Cancelled": "Ar Cealaigh ag an Úsáideoir",
    "Parameter Error": "Earráid Paraiméadair",
    "Failed to Select Image": "Theip ar Íomhá a Roghnú",
    "Generation Failed": "Theip ar Ghiniúint",
    "Generation Successful": "Giniúint Rathúil",
    "Generating": "Ag Giniúint",
    "Pending Generation": "Giniúint ar Feitheamh",
    "Unknown": "Anaithnid",
    "Feature in development, coming soon.": "Gné á forbairt, le teacht go luath.",

    # === Navigation ===
    "Calculate": "Ríomh",
    "Square": "Cearnóg",
    "Explore": "Taiscéal",
    "Mall": "Siopa",
    "Mine": "Mo Chuntas",

    # === Pages ===
    "Home": "Baile",
    "Fortune": "Fortún",
    "Compatibility": "Comhoiriúnacht",
    "Tarot": "Tarot",
    "Divination": "Tairngreacht",
    "Bazi": "Bází",
    "Annual": "Bliantúil",
    "Yearly": "Bliantúil",
    "Daily": "Laethúil",
    "Zodiac": "Stoidiaca",

    # === Settings ===
    "Settings": "Socruithe",
    "Language": "Teanga",
    "Theme": "Téama",
    "Notification": "Fógra",
    "Notifications": "Fógraí",
    "Privacy": "Príobháideachas",
    "About": "Eolas",
    "Help": "Cabhair",
    "Feedback": "Aiseolas",
    "Logout": "Logáil Amach",
    "Login": "Logáil Isteach",
    "Register": "Cláraigh",
    "Password": "Pasfhocal",
    "Email": "Ríomhphost",
    "Phone": "Fón",
    "Phone Number": "Uimhir Theileafóin",
    "Nickname": "Leasainm",
    "Gender": "Inscne",
    "Male": "Fireann",
    "Female": "Baineann",
    "Birthday": "Lá Breithe",
    "Date of Birth": "Dáta Breithe",
    "Time of Birth": "Am Breithe",
    "Place of Birth": "Áit Bhreithe",
    "Name": "Ainm",

    # === Account ===
    "Account": "Cuntas",
    "Account Info": "Eolas Cuntais",
    "Account Name": "Ainm Cuntais",
    "Account ID": "Aitheantas Cuntais",
    "Balance": "Iarmhéid",
    "Recharge": "Athluchtú",
    "History": "Stair",
    "Records": "Taifid",

    # === VIP ===
    "VIP": "VIP",
    "Member": "Ball",
    "Membership": "Ballraíocht",
    "Benefits": "Sochair",
    "Premium": "Préimh",
    "Subscribe": "Suibscrfobh",
    "Subscription": "Suibscrfobh",
    "Renew": "Athnuaigh",
    "Expire": "Éag",
    "Expired": "Éagtha",
    "Trial": "Triail",
    "Free": "Saor in Aisce",
}

# Special strings that contain apostrophes - use double quotes
EN_TO_GA_APOS = {
    "Success": 'D\'éirigh Leis',
}

def has_apostrophe(s):
    """Check if string contains an apostrophe"""
    return "'" in s

def needs_double_quotes(s):
    """Check if Irish string needs double quotes (has apostrophe)"""
    return has_apostrophe(s)

def build_quote_aware_replacement(english_val, irish_val):
    """Build a function that replaces English value with Irish, using correct quotes"""
    irish_needs_dq = needs_double_quotes(irish_val)
    quote_char = '"' if irish_needs_dq else "'"
    
    # Escape special regex chars in english_val
    escaped = re.escape(english_val)
    
    # Match with either single or double quotes in the source
    # Pattern: [whitespace]: '[english]' or "english"
    return escaped, irish_val, quote_char

def translate_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    result = []
    translated_count = 0
    
    # Build translation map sorted by length (longest first to avoid partial matches)
    sorted_vals = sorted(EN_TO_GA.keys(), key=len, reverse=True)
    
    for line in lines:
        # Skip comment lines and empty lines
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped == '':
            result.append(line)
            continue
        if stripped == '};' or stripped == 'export default {' or stripped.startswith('/**'):
            result.append(line)
            continue
        if stripped == '}':
            result.append(line)
            continue
        
        # Check if line contains a value assignment: key: 'value' or key: "value"
        # Pattern: optional whitespace, key, :, optional whitespace, 'value' or "value"
        val_match = re.match(r'^(\s*[\w]+\s*:\s*)(\'[^\']*\'|"[^"]*")(,?\s*)$', line)
        
        if val_match:
            prefix = val_match.group(1)
            old_val_str = val_match.group(2)
            suffix = val_match.group(3)
            
            # Extract the English value without quotes
            if old_val_str.startswith("'"):
                english_val = old_val_str[1:-1]
                old_quote = "'"
            else:
                english_val = old_val_str[1:-1]
                old_quote = '"'
            
            # Check if this value is in our dictionary
            if english_val in EN_TO_GA:
                irish_val = EN_TO_GA[english_val]
                # Use double quotes if Irish has apostrophe
                if needs_double_quotes(irish_val):
                    new_val_str = '"' + irish_val + '"'
                else:
                    new_val_str = "'" + irish_val + "'"
                
                new_line = prefix + new_val_str + suffix
                result.append(new_line)
                translated_count += 1
            else:
                result.append(line)
        else:
            result.append(line)
    
    output = '\n'.join(result)
    
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Translated {translated_count} strings")
    return translated_count

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '/Users/mo/Documents/uniapp/guojisuansuan/utils/locale/ga-IE.js'
    count = translate_file(path)
    print(f"Done. Translated {count} strings.")
