import random
import time
import pandas as pd
import re
from playwright.sync_api import sync_playwright


SEASONS = list(range(2024, 2009, -1)) 
PLAYOFF_LEAGUES = ["ISRF", "ISRA"] 
OUTPUT_FILE = "israel_playoffs_2010_2024.csv"

def get_rank(text_list, index):
    try:
        if index < len(text_list):
            return text_list[index].replace('(', '').replace(')', '').replace('.', '').strip()
    except:
        return None

def scrape_transfermarkt_playoffs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        headers = ["Season", "Matchday", "Date", "Home_Team", "Home_Rank", "Away_Team", "Away_Rank", "Score", "Attendance"]
        pd.DataFrame(columns=headers).to_csv(OUTPUT_FILE, index=False)

        for season in SEASONS:
            for league_id in PLAYOFF_LEAGUES:
                print(f"--- Scraping {league_id} Playoffs for Season {season} ---")
                
                for matchday in range(1, 11):
                    url = f"https://www.transfermarkt.com/ligat-haal/spieltag/wettbewerb/{league_id}/saison_id/{season}/spieltag/{matchday}"
                    
                    try:
                        print(f"  Checking Matchday {matchday}...")
                        page.goto(url, timeout=60000)
                        
                        try:
                            page.wait_for_selector("div.box", state="visible", timeout=5000)
                        except:
                            print(f"    No data for MD{matchday}. Moving on.")
                            continue

                        match_boxes = page.locator("div.box").all()
                        day_data = []

                        for box in match_boxes:
                            if box.locator(".matchresult").count() == 0:
                                continue

                            score_text = box.locator(".matchresult").inner_text().strip()
                            if ":" not in score_text or "-:-" in score_text:
                                continue 

                            teams = box.locator(".spieltagsansicht-vereinsname.hide-for-small a")
                            if teams.count() < 2: continue 
                                    
                            home_team = teams.nth(0).get_attribute("title")
                            away_team = teams.nth(1).get_attribute("title")

                            ranks = box.locator("span.tabellenplatz").all_inner_texts()
                            home_rank = get_rank(ranks, 0)
                            away_rank = get_rank(ranks, 1)

                            date_str = "Unknown"
                            if box.locator("a[href*='/datum/']").count() > 0:
                                date_str = box.locator("a[href*='/datum/']").first.inner_text()

                            attendance = 0
                            if box.locator(".icon-zuschauer-zahl").count() > 0:
                                try:
                                    full_att_text = box.locator(".icon-zuschauer-zahl").first.locator("xpath=..").inner_text(timeout=1000)
                                    digits = re.findall(r'[\d\.]+', full_att_text)
                                    for d in digits:
                                        clean_d = d.replace('.', '')
                                        if clean_d.isdigit() and int(clean_d) > 100:
                                            attendance = int(clean_d)
                                            break
                                except: pass 

                            
                            adjusted_matchday = 26 + matchday

                            day_data.append({
                                "Season": season,
                                "Matchday": adjusted_matchday,
                                "Date": date_str,
                                "Home_Team": home_team,
                                "Home_Rank": home_rank,
                                "Away_Team": away_team,
                                "Away_Rank": away_rank,
                                "Score": score_text,
                                "Attendance": attendance
                            })

                        if day_data:
                            pd.DataFrame(day_data).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
                            print(f"    Saved {len(day_data)} playoff matches.")

                        time.sleep(random.uniform(1.5, 3.0))

                    except Exception as e:
                        print(f"    Error: {e}")
                        time.sleep(3)

        browser.close()
        print("Playoff Scraping Complete!")

if __name__ == "__main__":
    scrape_transfermarkt_playoffs()