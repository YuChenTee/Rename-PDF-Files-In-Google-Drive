from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import fitz
import glob

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

directory = os.path.dirname(os.path.abspath("rename"))
print(os.listdir(directory))

new_name = ""
file_dir = None
file_name = ""
new_date = ""
tag_num = ""

#to access the file to get FILE NAME
def get_name_and_dir():
    global new_name, file_dir, file_name, new_date, tag_num
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)

            # to open file in readable format
            pdf = fitz.open(pdf_path)
            first_page = pdf[0] # get the first page

            # to extract info
            text = first_page.get_text()

            # to split texts into lines
            lines = text.split("\n")
            print(lines)

            # file name is next line of "FILE NAME"
            for i in range(len(lines)):
                if "FILE NAME" in lines[i]:
                    file_name = lines[i+1]
                    break
                else:
                    file_name = ""
                print(file_name)
            for i in range(len(lines)):
                if "Date/Time" in lines[i]:
                    new_date = lines[i+1]
                    break
                else:
                    new_date = ""
            for i in range(len(lines)):
                if "Tag Number" in lines[i]:
                    tag_num = lines[i+1]
                    break
                else:
                    tag_num = ""
            new_name = f"{new_date} {file_name} {tag_num}.pdf"

            # company name is next line of "COMPANY  NAME"
            for i in range(len(lines)):
                if "WORK" in lines[i]:
                    file_dir = lines[i+1]
                    break
                else:
                    file_dir = None
                print(file_dir)



# delete files after renaming
def delete_files():
    folder_path = "./"
    pdf_files = glob.glob(folder_path + "*.pdf")

    for file_path in pdf_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_path} deleted successfully")

# View all folders and file in your Google Drive
fileList_drive = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

for file in fileList_drive:

  # Get the folder ID that you want
  if(file['title'] == "SERVICE"):
    fileID = file["id"]
    target_file = drive.CreateFile({'id': fileID}) #create a file object to access into the test folder
    filelist_service = drive.ListFile({'q': f"'{fileID}' in parents and trashed=false"}).GetList() # Get the list of files in test folder

    for pdf_file in filelist_service:
        if (pdf_file["title"]).endswith(".pdf"):
            pdf_file["title"] = "aaa.pdf"
            target_file2= drive.CreateFile({'id': pdf_file["id"]}) #create file object for each pdf files in test folder
            try:
                target_file2.GetContentFile(pdf_file["title"], mimetype='pdf') #download the files
            except FileNotFoundError as e:
                print(e)
            get_name_and_dir()

            # to move the files into respective folders
            if file_dir is not None:
                for folder in filelist_service:
                    if folder["title"] == file_dir:
                        destination_id = folder["id"]
                        destination_folder = drive.CreateFile({'id': destination_id})
                        pdf_file['parents'] = [destination_folder]


            # rename the file in google drive
            pdf_file['title'] = new_name
            print(new_name)
            pdf_file.Upload({'convert': False})

            delete_files()







