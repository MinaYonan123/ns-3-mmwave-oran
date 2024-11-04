#include <iostream>
#include <string>
#include <curl/curl.h>
#include <jsoncpp/json/json.h>

using namespace std;

// Callback function to handle curl's response
size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    static_cast<string *> (userp)->append(static_cast<char *> (contents), size * nmemb);
    return size * nmemb;
}

// Function to perform CURL request
bool performCurlRequest(const string& url, string& response) {
    CURL *curl = curl_easy_init();
    if (!curl) {
        cerr << "Failed to initialize CURL" << endl;
        return false;
    }
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    if (res != CURLE_OK) {
        cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << endl;
        return false;
    }
    return true;
}

// Function to parse JSON response
bool parseJsonResponse(const string& jsonResponse, Json::Value& parsedRoot) {
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errs;
    bool parsingSuccessful = reader->parse(jsonResponse.c_str(),
        jsonResponse.c_str() + jsonResponse.size(), &parsedRoot, &errs);
    delete reader;
    if (!parsingSuccessful) {
        cerr << "Failed to parse JSON: " << errs << endl;
        return false;
    }
    return true;
}

int main() {
    string api_url = "http://localhost:9000/a1-p/policytypes/20008";
    string response;
    curl_global_init(CURL_GLOBAL_DEFAULT);
    if (performCurlRequest(api_url, response)) {
        Json::Value root;
        if (parseJsonResponse(response, root)) {
            cout << root.toStyledString();
            const Json::Value& quotes = root;
            cout << quotes["name"] << endl;
            cout << quotes["policy_type_id"] << endl;
        }
    }
    curl_global_cleanup();
    return 0;
}
