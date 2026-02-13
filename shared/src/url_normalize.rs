/// Normalizes a URL by uppercasing, removing protocol and www prefix.
///
/// Returns (normalized_name, protocol).
///
/// # Examples
/// - `"https://www.Google.com"` -> `("GOOGLE.COM", "HTTPS://")`
/// - `"http://example.org"` -> `("EXAMPLE.ORG", "HTTP://")`
pub fn normalize_url(url: &str) -> (String, String) {
    let upper = url.to_uppercase();
    let (stripped, proto) = if let Some(rest) = upper.strip_prefix("HTTPS://") {
        (rest, "HTTPS://")
    } else if let Some(rest) = upper.strip_prefix("HTTP://") {
        (rest, "HTTP://")
    } else {
        (upper.as_str(), "HTTP://")
    };
    let name = stripped
        .strip_prefix("WWW.")
        .unwrap_or(stripped)
        .to_string();
    (name, proto.to_string())
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

    #[test]
    fn test_normalize_preserves_www_in_subdomain() {
        let (name, proto) = normalize_url("https://subdomain.www.example.com");
        assert_eq!(name, "SUBDOMAIN.WWW.EXAMPLE.COM");
        assert_eq!(proto, "HTTPS://");
    }
}
