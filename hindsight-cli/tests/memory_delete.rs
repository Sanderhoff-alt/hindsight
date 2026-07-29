use serde_json::Value;
use std::io::{Read, Write};
use std::net::TcpListener;
use std::process::{Command, Output};
use std::sync::mpsc::{self, Receiver};
use std::thread::JoinHandle;

struct TestServer {
    url: String,
    request: Receiver<String>,
    handle: JoinHandle<()>,
}

fn start_test_server(response_body: &str) -> TestServer {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind test server");
    let address = listener.local_addr().expect("read test server address");
    let response_body = response_body.to_string();
    let (request_sender, request) = mpsc::channel();

    let handle = std::thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept CLI request");
        let mut bytes = Vec::new();
        let mut buffer = [0_u8; 4096];
        let mut expected_length = None;

        loop {
            let count = stream.read(&mut buffer).expect("read CLI request");
            if count == 0 {
                break;
            }
            bytes.extend_from_slice(&buffer[..count]);

            if expected_length.is_none() {
                if let Some(header_end) = bytes.windows(4).position(|window| window == b"\r\n\r\n")
                {
                    let headers = String::from_utf8_lossy(&bytes[..header_end]);
                    let content_length = headers
                        .lines()
                        .find_map(|line| {
                            let (name, value) = line.split_once(':')?;
                            name.eq_ignore_ascii_case("content-length").then(|| {
                                value.trim().parse::<usize>().expect("valid content length")
                            })
                        })
                        .unwrap_or(0);
                    expected_length = Some(header_end + 4 + content_length);
                }
            }

            if expected_length.is_some_and(|length| bytes.len() >= length) {
                break;
            }
        }

        request_sender
            .send(String::from_utf8(bytes).expect("UTF-8 CLI request"))
            .expect("capture CLI request");

        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            response_body.len(),
            response_body
        );
        stream
            .write_all(response.as_bytes())
            .expect("write API response");
    });

    TestServer {
        url: format!("http://{}", address),
        request,
        handle,
    }
}

fn run_delete(api_url: &str, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_hindsight"))
        .env("HINDSIGHT_API_URL", api_url)
        .env_remove("HINDSIGHT_API_KEY")
        .args(args)
        .output()
        .expect("run hindsight CLI")
}

#[test]
fn single_memory_delete_uses_delete_endpoint() {
    let memory_id = "11111111-1111-1111-1111-111111111111";
    let server =
        start_test_server(r#"{"success":true,"deleted_count":1,"message":"Memory unit deleted"}"#);

    let output = run_delete(
        &server.url,
        &[
            "memory", "delete", "bank-a", memory_id, "--yes", "--output", "json",
        ],
    );
    assert!(
        output.status.success(),
        "CLI failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let request = server.request.recv().expect("receive CLI request");
    server.handle.join().expect("join test server");
    assert!(
        request.starts_with(&format!(
            "DELETE /v1/default/banks/bank-a/memories/{} HTTP/1.1",
            memory_id
        )),
        "unexpected request: {request}"
    );

    let result: Value = serde_json::from_slice(&output.stdout).expect("JSON CLI output");
    assert_eq!(result["deleted_count"], 1);
}

#[test]
fn multiple_memory_delete_uses_bulk_post_endpoint() {
    let first_id = "11111111-1111-1111-1111-111111111111";
    let second_id = "22222222-2222-2222-2222-222222222222";
    let server =
        start_test_server(r#"{"success":true,"deleted_count":2,"message":"Memory units deleted"}"#);

    let output = run_delete(
        &server.url,
        &[
            "memory", "delete", "bank-a", first_id, second_id, "--yes", "--output", "json",
        ],
    );
    assert!(
        output.status.success(),
        "CLI failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let request = server.request.recv().expect("receive CLI request");
    server.handle.join().expect("join test server");
    assert!(
        request.starts_with("POST /v1/default/banks/bank-a/memories/bulk-delete HTTP/1.1"),
        "unexpected request: {request}"
    );
    let body = request.split_once("\r\n\r\n").expect("HTTP request body").1;
    let request_body: Value = serde_json::from_str(body).expect("JSON request body");
    assert_eq!(
        request_body["unit_ids"],
        serde_json::json!([first_id, second_id])
    );

    let result: Value = serde_json::from_slice(&output.stdout).expect("JSON CLI output");
    assert_eq!(result["deleted_count"], 2);
}

#[test]
fn memory_delete_requires_confirmation_by_default() {
    let output = run_delete(
        "http://127.0.0.1:1",
        &[
            "memory",
            "delete",
            "bank-a",
            "11111111-1111-1111-1111-111111111111",
        ],
    );

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("This cannot be undone"));
    assert!(stdout.contains("Operation cancelled"));
}
