async function saveWebpage() {
  try {
    const tabs = await browser.tabs.query({ active: true, currentWindow: true });
    const tab = tabs[0];

    const response = await fetch(tab.url);
    const text = await response.text();

    const payload = {
      url: tab.url,
      title: tab.title,
      content: text
    };

    const saveResponse = await fetch('http://localhost:5000/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const result = await saveResponse.json();
    console.log(result.message);

  } catch (error) {
    console.error('Error saving webpage:', error);
  }
}

browser.browserAction.onClicked.addListener(saveWebpage);
