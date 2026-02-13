use regex::Regex;
use reqwest::Client;
use std::sync::LazyLock;
use std::time::{Duration, Instant};

static URL_REGEX: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"https?://[\w\-.]+").unwrap());

pub struct PageData {
    pub html: String,
    pub elapsed: Duration,
}

/// Fetches a URL and returns its HTML content and elapsed time.
/// Returns None on any failure (matching Python's ('', '') return).
pub async fn get_page_data(client: &Client, url: &str) -> Option<PageData> {
    let start = Instant::now();
    let response = client.get(url).send().await.ok()?;
    let html = response.text().await.ok()?;
    Some(PageData {
        html,
        elapsed: start.elapsed(),
    })
}

/// Extracts URLs from HTML content using the same regex as the Python feeder.
/// Pattern: `https?://[\w\-.]+` — captures protocol + domain only (no paths).
pub fn extract_urls(html: &str) -> Vec<String> {
    URL_REGEX
        .find_iter(html)
        .map(|m| m.as_str().to_string())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_urls_basic() {
        let html = r#"<a href="https://google.com">link</a> and http://example.org too"#;
        let urls = extract_urls(html);
        assert_eq!(urls, vec!["https://google.com", "http://example.org"]);
    }

    #[test]
    fn test_extract_urls_strips_paths() {
        let html = "Visit https://example.com/path/to/page for more";
        let urls = extract_urls(html);
        // Regex only captures domain, /path/to/page has '/' which isn't in [\w\-.]
        assert_eq!(urls, vec!["https://example.com"]);
    }

    #[test]
    fn test_extract_urls_empty() {
        assert!(extract_urls("no urls here").is_empty());
    }

    #[test]
    fn test_extract_urls_multiple_same_page() {
        let html = "https://a.com https://b.com http://c.org https://a.com";
        let urls = extract_urls(html);
        assert_eq!(
            urls,
            vec!["https://a.com", "https://b.com", "http://c.org", "https://a.com"]
        );
    }

    #[test]
    fn test_extract_urls_with_hyphens_and_dots() {
        let html = "https://my-site.co.uk and http://sub.example-domain.com";
        let urls = extract_urls(html);
        assert_eq!(
            urls,
            vec!["https://my-site.co.uk", "http://sub.example-domain.com"]
        );
    }
}
