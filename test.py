

def main(title):
    if "," in title:
        list = title.split(",")
    else:
        list = title

    for item in list:
        print(item.strip())
if __name__ == "__main__":
    title = input("Enter the title of the job: ")
    main(title)