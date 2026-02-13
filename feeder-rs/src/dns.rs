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
