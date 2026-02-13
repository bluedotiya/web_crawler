use hickory_resolver::TokioResolver;
use std::net::IpAddr;

use crate::error::FeederError;

pub struct NetworkStats {
    pub domain: String,
    pub ip: String,
}

/// Resolves a normalized URL (already uppercased, no protocol) to domain and IPv4 address.
///
/// Matches the Python feeder's iterative domain shortening logic:
/// For "A.B.C.COM", tries "C.COM", then "B.C.COM", then "A.B.C.COM", etc.
/// up to max_depth iterations.
///
/// Bug #2 fix: returns proper Result::Err instead of undefined variable.
pub async fn get_network_stats(
    resolver: &TokioResolver,
    normalized_url: &str,
    max_depth: usize,
) -> Result<NetworkStats, FeederError> {
    let parts: Vec<&str> = normalized_url.split('.').collect();

    for suffix_len in 2..=max_depth.min(parts.len()) {
        let start = parts.len().saturating_sub(suffix_len);
        let domain_parts = &parts[start..];
        let domain = domain_parts.join(".");

        // DNS queries require lowercase
        match resolver.lookup_ip(domain.to_lowercase().as_str()).await {
            Ok(lookup) => {
                if let Some(ip) = lookup.iter().find_map(|addr| match addr {
                    IpAddr::V4(v4) => Some(v4.to_string()),
                    _ => None,
                }) {
                    return Ok(NetworkStats {
                        domain: domain_parts[0].to_string(),
                        ip,
                    });
                }
            }
            Err(_) => continue,
        }
    }

    Err(FeederError::DnsResolution {
        domain: normalized_url.to_string(),
        attempts: max_depth as u32,
    })
}

#[cfg(test)]
mod tests {
    /// Builds candidate domains from a normalized URL by progressively including
    /// more subdomains from right to left, starting with the TLD+1.
    ///
    /// E.g. "A.B.C.COM" with max_depth=5 -> ["C.COM", "B.C.COM", "A.B.C.COM"]
    fn build_candidate_domains(normalized_url: &str, max_depth: usize) -> Vec<String> {
        let parts: Vec<&str> = normalized_url.split('.').collect();
        (2..=max_depth.min(parts.len()))
            .map(|suffix_len| {
                let start = parts.len().saturating_sub(suffix_len);
                parts[start..].join(".")
            })
            .collect()
    }
    use super::*;

    #[test]
    fn test_candidates_simple_domain() {
        let candidates = build_candidate_domains("GOOGLE.COM", 5);
        assert_eq!(candidates, vec!["GOOGLE.COM"]);
    }

    #[test]
    fn test_candidates_subdomain() {
        let candidates = build_candidate_domains("API.GOOGLE.COM", 5);
        assert_eq!(candidates, vec!["GOOGLE.COM", "API.GOOGLE.COM"]);
    }

    #[test]
    fn test_candidates_deep_subdomain() {
        let candidates = build_candidate_domains("A.B.C.COM", 5);
        assert_eq!(candidates, vec!["C.COM", "B.C.COM", "A.B.C.COM"]);
    }

    #[test]
    fn test_candidates_respects_max_depth() {
        let candidates = build_candidate_domains("A.B.C.D.COM", 3);
        assert_eq!(candidates, vec!["D.COM", "C.D.COM"]);
    }

    #[test]
    fn test_candidates_single_part() {
        let candidates = build_candidate_domains("LOCALHOST", 5);
        assert!(candidates.is_empty());
    }

    #[tokio::test]
    async fn test_get_network_stats_known_domain() {
        let resolver = TokioResolver::builder_tokio().unwrap().build();
        let result = get_network_stats(&resolver, "GOOGLE.COM", 5).await;
        assert!(result.is_ok());
        let stats = result.unwrap();
        assert_eq!(stats.domain, "GOOGLE");
        assert!(!stats.ip.is_empty());
    }

    #[tokio::test]
    async fn test_get_network_stats_nonexistent_domain() {
        let resolver = TokioResolver::builder_tokio().unwrap().build();
        let result = get_network_stats(&resolver, "THIS.DOMAIN.DOES.NOT.EXIST.INVALID", 5).await;
        assert!(result.is_err());
    }
}
