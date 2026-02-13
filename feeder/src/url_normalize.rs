/// Normalizes a URL by uppercasing, removing protocol and www prefix.
///
/// Returns (normalized_name, protocol) matching the Python feeder behavior.
///
/// # Examples
/// - `"https://www.Google.com"` -> `("GOOGLE.COM", "HTTPS://")`
/// - `"http://example.org"` -> `("EXAMPLE.ORG", "HTTP://")`
pub fn normalize_url(url: &str) -> (String, String) {
    let upper = url.to_uppercase();
    if upper.contains("HTTPS://") {
        let name = upper.replace("HTTPS://", "").replace("WWW.", "");
        (name, "HTTPS://".to_string())
    } else {
        let name = upper.replace("HTTP://", "").replace("WWW.", "");
        (name, "HTTP://".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize_https_with_www() {
        let (name, proto) = normalize_url("https://www.Google.com");
        assert_eq!(name, "GOOGLE.COM");
        assert_eq!(proto, "HTTPS://");
    }

    #[test]
    fn test_normalize_http_no_www() {
        let (name, proto) = normalize_url("http://example.org");
        assert_eq!(name, "EXAMPLE.ORG");
        assert_eq!(proto, "HTTP://");
    }

    #[test]
    fn test_normalize_https_no_www() {
        let (name, proto) = normalize_url("https://google.com");
        assert_eq!(name, "GOOGLE.COM");
        assert_eq!(proto, "HTTPS://");
    }

    #[test]
    fn test_normalize_preserves_subdomains() {
        let (name, proto) = normalize_url("https://api.sub.example.com");
        assert_eq!(name, "API.SUB.EXAMPLE.COM");
        assert_eq!(proto, "HTTPS://");
    }

    #[test]
    fn test_normalize_http_with_www() {
        let (name, proto) = normalize_url("http://www.example.com");
        assert_eq!(name, "EXAMPLE.COM");
        assert_eq!(proto, "HTTP://");
    }
}
