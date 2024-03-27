import os

def combine_html_files(directory):
    # Open a new text file for writing the combined content
    with open('all_HTMLs_combined.txt', 'w', encoding='utf-8') as combined_file:

        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                # Write the full name and extension of the file to the combined file
                combined_file.write(f"{filename}\n")
                combined_file.write(":\n")
                
                # Open the .html file and append its content to the combined file
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                    content = file.read()
                    combined_file.write(content)
                    combined_file.write("\n\n\n")  # Add three newlines after each file's content

    print("Combined text file from HTML files created successfully!")

# Call the function with the directory of your .html files
combine_html_files('.')
