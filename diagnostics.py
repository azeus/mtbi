# diagnostics.py - Complete diagnostics module for MBTI app

import streamlit as st
import os
import sys
import time
import importlib
import pkg_resources
import socket
import json
import traceback


def run_comprehensive_diagnostics():
    """Run comprehensive system diagnostics for the MBTI app."""
    results = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "streamlit_available": True,
        "packages": check_packages(),
        "secrets": check_secrets(),
        "weaviate": check_weaviate_connection(),
        "openai": check_openai()
    }

    return results


def check_packages():
    """Check if all required packages are installed."""
    required_packages = {
        "streamlit": "1.30.0",
        "weaviate-client": "3.26.7",
        "openai": "1.3.0",
        "python-dotenv": "1.0.0",
        "llama-index": "0.8.34"
    }

    results = {}
    for package, version in required_packages.items():
        package_name = package.replace("-", "_")
        try:
            # First try to check with pkg_resources
            try:
                actual_version = pkg_resources.get_distribution(package).version
                installed = True
            except pkg_resources.DistributionNotFound:
                # Then try to import
                try:
                    imported = importlib.import_module(package_name)
                    actual_version = getattr(imported, "__version__", "Unknown")
                    installed = True
                except ImportError:
                    installed = False
                    actual_version = None
        except Exception as e:
            installed = False
            actual_version = f"Error: {str(e)}"

        results[package] = {
            "installed": installed,
            "required_version": version,
            "actual_version": actual_version,
            "status": "OK" if installed and (actual_version and version in str(actual_version)) else
            "Version mismatch" if installed else "Not installed"
        }

    return results


def check_secrets():
    """Check if all required secrets are configured."""
    required_secrets = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]

    results = {}
    # Check Streamlit secrets
    if hasattr(st, 'secrets'):
        for secret in required_secrets:
            value = None
            try:
                value = st.secrets.get(secret)
            except:
                pass

            results[f"{secret}_in_secrets"] = {
                "present": value is not None,
                "status": "OK" if value else "Missing"
            }

    # Check environment variables
    for secret in required_secrets:
        value = os.getenv(secret)
        results[f"{secret}_in_env"] = {
            "present": value is not None,
            "status": "OK" if value else "Missing"
        }

    # Additional validation for URL format
    weaviate_url = None
    if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets:
        weaviate_url = st.secrets.get('WEAVIATE_URL')
    else:
        weaviate_url = os.getenv("WEAVIATE_URL")

    if weaviate_url:
        results["WEAVIATE_URL_format"] = {
            "present": True,
            "valid_format": weaviate_url.startswith(("http://", "https://")),
            "status": "OK" if weaviate_url.startswith(
                ("http://", "https://")) else "Invalid format - missing http:// or https://"
        }

    return results


def check_weaviate_connection():
    """Test Weaviate connection directly."""
    results = {
        "module_available": False,
        "url_accessible": False,
        "auth_working": False,
        "detailed_status": "Not tested"
    }

    # Check if weaviate module is available
    try:
        import weaviate
        results["module_available"] = True
        results["weaviate_version"] = getattr(weaviate, "__version__", "Unknown")
    except ImportError:
        results["detailed_status"] = "Weaviate client module not installed"
        return results
    except Exception as e:
        results["detailed_status"] = f"Error importing weaviate: {str(e)}"
        return results

    # Get Weaviate URL and API key
    weaviate_url = None
    weaviate_api_key = None

    if hasattr(st, 'secrets'):
        try:
            weaviate_url = st.secrets.get('WEAVIATE_URL')
            weaviate_api_key = st.secrets.get('WEAVIATE_API_KEY')
        except:
            pass

    if not weaviate_url:
        weaviate_url = os.getenv("WEAVIATE_URL")
    if not weaviate_api_key:
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    if not weaviate_url:
        results["detailed_status"] = "No Weaviate URL configured"
        return results

    # Check if URL format is valid
    if not weaviate_url.startswith(("http://", "https://")):
        results["detailed_status"] = f"Invalid URL format: {weaviate_url} - Missing http:// or https://"
        return results

    # Parse URL to get hostname for basic connectivity test
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(weaviate_url)
        hostname = parsed_url.netloc.split(':')[0]

        # Try to resolve hostname
        try:
            socket.gethostbyname(hostname)
            results["hostname_resolves"] = True
        except:
            results["hostname_resolves"] = False
            results["detailed_status"] = f"Cannot resolve hostname: {hostname}"
            return results
    except Exception as e:
        results["detailed_status"] = f"Error parsing URL: {str(e)}"
        return results

    # Test basic connectivity via HTTP request
    try:
        import requests
        try:
            # Disable SSL verification temporarily for testing
            health_url = f"{weaviate_url}/.well-known/ready"
            response = requests.get(health_url, timeout=5, verify=True)
            results["url_accessible"] = response.status_code < 500  # Consider it accessible if not a server error

            if response.status_code in (200, 401, 403):
                results["detailed_status"] = f"URL accessible, status code: {response.status_code}"
            else:
                results["detailed_status"] = f"URL accessible but returned status code: {response.status_code}"
                return results
        except requests.exceptions.SSLError:
            # Try again without SSL verification for debugging
            try:
                response = requests.get(health_url, timeout=5, verify=False)
                results["url_accessible"] = True
                results["detailed_status"] = "URL accessible but SSL certificate validation failed"
            except Exception as e:
                results["detailed_status"] = f"SSL Error and connection failed without verification: {str(e)}"
                return results
        except Exception as e:
            results["detailed_status"] = f"Connection error: {str(e)}"
            return results
    except ImportError:
        results["detailed_status"] = "Requests module not available for HTTP testing"
        # Continue with weaviate client test anyway

    # Try to connect with the weaviate client
    try:
        # Create authentication object based on available version
        try:
            # Try modern auth approach first
            from weaviate.auth import AuthApiKey
            auth_config = AuthApiKey(api_key=weaviate_api_key)
        except ImportError:
            # Fallback for older versions
            auth_config = {"api_key": weaviate_api_key}

        # Setup OpenAI API key if available
        openai_api_key = None
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            openai_api_key = st.secrets.get('OPENAI_API_KEY')
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        additional_headers = {}
        if openai_api_key:
            additional_headers["X-OpenAI-Api-Key"] = openai_api_key

        # Initialize client with different approaches based on version
        client = None
        exceptions = []

        # Try approach 1 - newest Weaviate client
        try:
            client = weaviate.Client(
                url=weaviate_url,
                auth_client=auth_config,
                additional_headers=additional_headers
            )
        except Exception as e:
            exceptions.append(f"Modern client init failed: {str(e)}")

        # Try approach 2 - older Weaviate client
        if client is None:
            try:
                client = weaviate.Client(
                    url=weaviate_url,
                    auth_config=auth_config,
                    additional_headers=additional_headers
                )
            except Exception as e:
                exceptions.append(f"Legacy client init failed: {str(e)}")

        # Try approach 3 - minimal params
        if client is None:
            try:
                client = weaviate.Client(weaviate_url)
            except Exception as e:
                exceptions.append(f"Minimal client init failed: {str(e)}")
                results["detailed_status"] = f"All client initialization approaches failed: {'; '.join(exceptions)}"
                return results

        # Test client functionality
        if client is not None:
            # Check if is_ready method exists and try to use it
            if hasattr(client, "is_ready") and callable(getattr(client, "is_ready")):
                try:
                    if client.is_ready():
                        results["auth_working"] = True
                        results["detailed_status"] = "Connected successfully with is_ready()"

                        # Try to get version info
                        try:
                            meta = client.get_meta()
                            results["weaviate_server_version"] = meta.get("version", "Unknown")
                        except:
                            pass

                        return results
                    else:
                        results["detailed_status"] = "Connection established but is_ready() returned False"
                except Exception as e:
                    results["detailed_status"] = f"Error checking readiness: {str(e)}"

            # Fallback: try to get schema as a connection test
            try:
                schema = client.schema.get()
                if schema is not None:
                    results["auth_working"] = True
                    results["detailed_status"] = "Connected successfully with schema.get()"
                    return results
            except Exception as e:
                results["detailed_status"] = f"Error getting schema: {str(e)}"

    except Exception as e:
        results["detailed_status"] = f"Error in Weaviate client test: {str(e)}"
        results["traceback"] = traceback.format_exc()

    return results


def check_openai():
    """Test OpenAI API connection."""
    results = {
        "module_available": False,
        "api_key_configured": False,
        "api_working": False,
        "detailed_status": "Not tested"
    }

    # Check if OpenAI module is available
    try:
        import openai
        results["module_available"] = True
        results["openai_version"] = getattr(openai, "__version__", "Unknown")
    except ImportError:
        results["detailed_status"] = "OpenAI module not installed"
        return results
    except Exception as e:
        results["detailed_status"] = f"Error importing OpenAI: {str(e)}"
        return results

    # Get OpenAI API key
    openai_api_key = None
    if hasattr(st, 'secrets'):
        try:
            openai_api_key = st.secrets.get('OPENAI_API_KEY')
        except:
            pass

    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        results["detailed_status"] = "No OpenAI API key configured"
        return results

    results["api_key_configured"] = True

    # Test API connection - handle different module versions
    try:
        # Try the newer client approach first
        try:
            from openai import OpenAI
            # Only use the API key parameter to avoid proxies error
            client = OpenAI(api_key=openai_api_key)

            # Try a simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )

            results["api_working"] = True
            results["detailed_status"] = "API working correctly with new client"

        except Exception as e1:
            # Log the error from the new client attempt
            results["new_client_error"] = str(e1)

            # Try the legacy approach
            try:
                # Set the API key directly
                openai.api_key = openai_api_key

                # Try a simple completion with legacy API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )

                results["api_working"] = True
                results["detailed_status"] = "API working correctly with legacy client"

            except Exception as e2:
                results["legacy_client_error"] = str(e2)
                results["detailed_status"] = f"Both OpenAI client approaches failed. Latest error: {str(e2)}"

    except Exception as e:
        results["detailed_status"] = f"Unexpected error in OpenAI test: {str(e)}"
        results["traceback"] = traceback.format_exc()

    return results


def display_diagnostics_results(results):
    """Display diagnostics results in a readable format."""
    st.subheader("System Diagnostics Results")
    st.caption(f"Run at: {results.get('timestamp', 'unknown time')}")

    # Display system info
    st.write(f"Python version: {results.get('python_version', 'Unknown')}")

    # Display package status
    with st.expander("Package Status", expanded=True):
        for package, info in results.get('packages', {}).items():
            if info.get('status') == "OK":
                st.success(f"✅ {package}: {info.get('actual_version')}")
            elif info.get('status') == "Version mismatch":
                st.warning(f"⚠️ {package}: Found {info.get('actual_version')}, required {info.get('required_version')}")
            else:
                st.error(f"❌ {package}: Not installed (required {info.get('required_version')})")
                st.info(f"Run: pip install {package}=={info.get('required_version')}")

    # Display secrets status
    with st.expander("Credentials Status", expanded=True):
        # Check for URL format issues
        if 'WEAVIATE_URL_format' in results.get('secrets', {}):
            url_info = results['secrets']['WEAVIATE_URL_format']
            if not url_info.get('valid_format', False):
                st.error(f"❌ WEAVIATE_URL format error: {url_info.get('status')}")
                st.info("Make sure your URL starts with https:// or http://")

        # Check for secrets in streamlit
        st.write("**Streamlit Secrets:**")
        secret_found = False
        for key, info in results.get('secrets', {}).items():
            if key.endswith("_in_secrets") and info.get('present', False):
                st.success(f"✅ {key.replace('_in_secrets', '')}")
                secret_found = True

        if not secret_found:
            st.error("❌ No credentials found in Streamlit secrets")
            st.info("Create a .streamlit/secrets.toml file with your credentials")

        # Check for env vars
        st.write("**Environment Variables:**")
        env_found = False
        for key, info in results.get('secrets', {}).items():
            if key.endswith("_in_env") and info.get('present', False):
                st.success(f"✅ {key.replace('_in_env', '')}")
                env_found = True

        if not env_found:
            st.warning("⚠️ No credentials found in environment variables")

    # Display Weaviate status
    with st.expander("Weaviate Status", expanded=True):
        weaviate_info = results.get('weaviate', {})

        if not weaviate_info.get('module_available', False):
            st.error(f"❌ Weaviate client module not available")
            st.info("Run: pip install weaviate-client==3.26.7")
        else:
            st.success(f"✅ Weaviate client module available: {weaviate_info.get('weaviate_version', 'Unknown')}")

        if weaviate_info.get('auth_working', False):
            st.success(f"✅ Weaviate connection successful")
            if "weaviate_server_version" in weaviate_info:
                st.info(f"Weaviate server version: {weaviate_info['weaviate_server_version']}")
        elif weaviate_info.get('url_accessible', False):
            st.warning(f"⚠️ Weaviate URL accessible but authentication failed")
        else:
            st.error(f"❌ Weaviate connection failed")

        st.write(f"Details: {weaviate_info.get('detailed_status', 'No details available')}")

        if weaviate_info.get('traceback'):
            with st.expander("Weaviate Error Details", expanded=False):
                st.code(weaviate_info['traceback'], language="python")

    # Display OpenAI status
    with st.expander("OpenAI Status", expanded=True):
        openai_info = results.get('openai', {})

        if not openai_info.get('module_available', False):
            st.error(f"❌ OpenAI module not available")
            st.info("Run: pip install openai==1.3.0")
        else:
            st.success(f"✅ OpenAI module available: {openai_info.get('openai_version', 'Unknown')}")

        if openai_info.get('api_working', False):
            st.success(f"✅ OpenAI API working correctly")
        elif openai_info.get('api_key_configured', False):
            st.warning(f"⚠️ OpenAI API key found but API test failed")
        else:
            st.error(f"❌ OpenAI API key not configured")

        st.write(f"Details: {openai_info.get('detailed_status', 'No details available')}")

        if 'new_client_error' in openai_info:
            with st.expander("OpenAI New Client Error", expanded=False):
                st.code(openai_info['new_client_error'], language="plain")

        if 'legacy_client_error' in openai_info:
            with st.expander("OpenAI Legacy Client Error", expanded=False):
                st.code(openai_info['legacy_client_error'], language="plain")

        if openai_info.get('traceback'):
            with st.expander("OpenAI Error Details", expanded=False):
                st.code(openai_info['traceback'], language="python")

    # Overall status and recommendation
    st.subheader("Overall Status")

    # Determine if everything is working
    weaviate_ok = results.get('weaviate', {}).get('auth_working', False)
    openai_ok = results.get('openai', {}).get('api_working', False)

    if weaviate_ok and openai_ok:
        st.success("✅ All systems operational! Your app should work in full advanced mode.")
    elif not weaviate_ok and not openai_ok:
        st.error("❌ Major issues detected. The app will run in simulation mode.")
        st.write("To fix: Configure both Weaviate and OpenAI credentials.")
    else:
        st.warning("⚠️ Partial functionality available.")
        if not weaviate_ok:
            st.write("- Weaviate connection issue: Check the URL and API key.")
        if not openai_ok:
            st.write("- OpenAI API issue: Verify your API key.")

    # Add clear instructions for fixing issues
    st.subheader("Recommendations")
    if not weaviate_ok or not openai_ok:
        st.write("Based on the diagnostics, here are specific steps to fix the issues:")

        # Package fixes
        package_issues = False
        for package, info in results.get('packages', {}).items():
            if info.get('status') != "OK":
                if not package_issues:
                    st.write("**Package fixes:**")
                    package_issues = True
                st.code(f"pip install {package}=={info.get('required_version')}", language="bash")

        # Weaviate URL format issue
        if 'WEAVIATE_URL_format' in results.get('secrets', {}) and not results['secrets']['WEAVIATE_URL_format'].get(
                'valid_format', True):
            st.write("**Fix Weaviate URL format in your secrets.toml:**")
            weaviate_url = None
            if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets:
                weaviate_url = st.secrets.get('WEAVIATE_URL')
            else:
                weaviate_url = os.getenv("WEAVIATE_URL")

            if weaviate_url:
                st.code(f'WEAVIATE_URL = "https://{weaviate_url}"', language="toml")

        # Missing secrets
        if not secret_found:
            st.write("**Create a secrets.toml file:**")
            st.code("""
# Save this in .streamlit/secrets.toml
WEAVIATE_URL = "https://your-weaviate-cluster-url"
WEAVIATE_API_KEY = "your-weaviate-api-key"
OPENAI_API_KEY = "your-openai-api-key"
            """, language="toml")


def show_setup_guide():
    """Display instructions for setting up credentials."""
    st.subheader("Setup Guide")

    st.write("""
    To use the MBTI Chat app in advanced mode with Weaviate and OpenAI, you need to configure your credentials.
    Here's how to set them up:
    """)

    with st.expander("Option 1: Streamlit Secrets (Recommended)", expanded=True):
        st.write("""
        1. Create a `.streamlit` directory in your project root if it doesn't exist
        2. Inside that directory, create a file named `secrets.toml`
        3. Add your credentials in this format:
        """)

        st.code("""
        WEAVIATE_URL = "https://your-weaviate-cluster-url"
        WEAVIATE_API_KEY = "your-weaviate-api-key"
        OPENAI_API_KEY = "your-openai-api-key"
        """, language="toml")

        st.write("""
        **Important details:**
        - Make sure to include the quotes around the values
        - The Weaviate URL must include the https:// prefix
        - Don't add a trailing slash to the URL
        - Don't include any additional parameters
        """)

        st.write("Note: After adding or updating secrets, you'll need to restart your Streamlit app.")

    with st.expander("Option 2: Environment Variables"):
        st.write("Set these environment variables before running the app:")

        st.code("""
        export WEAVIATE_URL="https://your-weaviate-cluster-url"
        export WEAVIATE_API_KEY="your-weaviate-api-key"
        export OPENAI_API_KEY="your-openai-api-key"
        """, language="bash")

        st.write("Then run your app normally with:")
        st.code("streamlit run app.py", language="bash")

    st.warning("""
    Important: Keep your API keys secure! Do not commit them to public repositories
    or share them with unauthorized users.
    """)

    # Example for fixing proxies error
    st.subheader("Common Errors and Fixes")

    with st.expander("OpenAI 'proxies' Error", expanded=True):
        st.write("""
        If you see an error like `Client.__init__() got an unexpected keyword argument 'proxies'`, 
        this means your OpenAI package version has a different interface than expected.
        """)

        st.code("pip install openai==1.3.0", language="bash")

        st.write("""
        Then update any code in your project that initializes the OpenAI client to only use 
        the api_key parameter without any other parameters like proxies.
        """)

    with st.expander("Weaviate Module Not Available", expanded=True):
        st.write("""
        If you see "Weaviate: Module not available", you need to install the weaviate-client package.
        """)

        st.code("pip install weaviate-client==3.26.7", language="bash")

        st.write("Make sure to restart your Streamlit app after installing.")

    with st.expander("SSL Certificate Verification Issues", expanded=True):
        st.write("""
        If you're having issues with SSL certificate verification when connecting to Weaviate, 
        you might need to update your certificate store or temporarily disable verification for testing.
        """)

        st.code("""
        # Option 1: Update certificates
        pip install --upgrade certifi

        # Option 2: For testing only (NOT RECOMMENDED FOR PRODUCTION)
        # Modify weaviate_connection.py to include:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        """, language="python")