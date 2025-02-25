import streamlit as st
import openai
import pandas as pd
import requests
import io

# Συνάρτηση για φόρτωση δεδομένων έργων
def load_projects_data():
    # Χρησιμοποίησε το raw URL του CSV αρχείου από το GitHub
    csv_url = "https://raw.githubusercontent.com/minassakkas/Streamlit-UI/main/Copy%20of%20ΕΣΗΔΗΣ.csv"
    
    try:
        response = requests.get(csv_url)
        response.raise_for_status()  # Έλεγχος αν υπάρχει πρόβλημα με το request
        
        # Προσπαθούμε πρώτα με UTF-8
        try:
            df = pd.read_csv(io.StringIO(response.text), sep=';', encoding="utf-8", on_bad_lines='skip', dtype=str)
        except UnicodeDecodeError:
            st.warning("⚠ Προσπάθεια ανάγνωσης με UTF-8 απέτυχε, δοκιμάζουμε με ISO-8859-7...")
            df = pd.read_csv(io.StringIO(response.text), sep=';', encoding="ISO-8859-7", on_bad_lines='skip', dtype=str)

    except Exception as e:
        st.error(f"Σφάλμα κατά το άνοιγμα του αρχείου: {e}")
        return None


    max_rows = 30
    df = df.head(max_rows)
    
    projects_data = []
    for _, row in df.iterrows():
        try:
            project = {
                "id": str(row.iloc[0]).strip() if pd.notnull(row.iloc[0]) else "",
                "name": str(row.iloc[1]).strip() if pd.notnull(row.iloc[1]) else "",
                "budget": str(row.iloc[3]).strip() if pd.notnull(row.iloc[3]) else "",
                "deadline": str(row.iloc[6]).strip() if pd.notnull(row.iloc[6]) else ""
            }
            if project["name"]:
                projects_data.append(project)
        except:
            continue
    
    return projects_data

# Streamlit UI
st.title("🔎 Αναζήτηση Διαγωνισμών")
st.write("Χρησιμοποίησε το chatbot για να βρεις δημοσιευμένους διαγωνισμούς που σε ενδιαφέρουν.")

openai_api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
user_input = st.text_area("Τι έργα ψάχνεις;")
submit = st.button("🔍 Αναζήτηση")

if submit:
    if not openai_api_key.startswith("sk-"):
        st.warning("Παρακαλώ εισάγετε ένα έγκυρο OpenAI API Key!", icon="⚠")
    else:
        projects_data = load_projects_data()
        if not projects_data:
            st.error("Δεν βρέθηκαν έργα ή υπήρξε πρόβλημα με το αρχείο CSV.")
        else:
            projects_formatted = "\n".join([
                f"{p['name']} | Προϋπολογισμός: {p['budget']} | Καταληκτική ημερομηνία: {p['deadline']} | ID: {p['id']}"
                for p in projects_data
            ])
            
            system_prompt = (
                "Καλώς ήρθες! Τι έργα ψάχνεις;\n\n"
                "Προτεινόμενα έργα:\n\n"
                "Δεδομένης της λίστας έργων που ακολουθεί, εντόπισε αυτά που είναι σχετικά με το αίτημα του χρήστη "
                "και εμφάνισέ τα στην παρακάτω μορφή, χωρίς πρόσθετα σχόλια:\n\n"
                "Όνομα έργου: <Όνομα έργου>\n"
                "Προϋπολογισμός: <Προϋπολογισμός>\n"
                "Καταληκτική ημερομηνία: <Καταληκτική ημερομηνία>\n"
                "Σύνδεσμος: https://nepps-search.eprocurement.gov.gr/actSearch/resources/search/<ID>\n\n"
            )

            user_message = (
                f"Η περιγραφή του χρήστη είναι: '{user_input}'\n\n"
                f"Η λίστα των διαθέσιμων έργων ({len(projects_data)} εγγραφές):\n{projects_formatted}\n\n"
                "Παρακαλώ επέλεξε τα πιο σχετικά έργα βάσει της παραπάνω περιγραφής."
            )

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                )
                answer = response['choices'][0]['message']['content']
                st.success("📋 Προτεινόμενα έργα:")
                st.write(answer)
            except Exception as e:
                st.error(f"Σφάλμα κατά την κλήση του OpenAI API: {e}")
